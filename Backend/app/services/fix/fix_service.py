import time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...models.fix import Fix
from ...models.user import User
from ...schemas.review import Finding
from ..agent.tools import Context
from ..github_service import get_token
from .github_files import branch_sha, commit_files, create_branch, delete_branch, get_pr, latest_run, open_pr, test_log
from .prompts import fix_agent, fix_prompt, retry_prompt
from .workflow import WORKFLOW_FILE, make_workflow


MAX_ATTEMPTS = 3
MAX_STEPS = 40


def make_fix(db: Session, user: User, repo: str, pr_number: int, finding: Finding):
    token = get_token(user, repo)
    pr = get_pr(token, repo, pr_number)
    context = Context(token=token, repo=repo, ref=pr["head"]["sha"])

    message = fix_prompt.format(
        title=finding.title,
        file=finding.file,
        line=finding.line,
        explanation=finding.explanation,
        suggestion=finding.suggestion,
    )
    result = run_agent(message, context)
    if len(context.changes) == 0:
        raise HTTPException(status_code=502, detail="AI could not make a fix for this problem")
    if result.test_file not in context.changes:
        result.test_file = ""
        result.test_command = ""

    fix = Fix(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        file=finding.file,
        title=finding.title,
        explanation=result.explanation,
        changes=[{"file": path, "old_code": context.originals[path], "new_code": code} for path, code in context.changes.items()],
        test_file=result.test_file,
        test_command=result.test_command,
    )
    db.add(fix)
    db.commit()
    db.refresh(fix)
    return fix


def run_agent(message: str, context: Context):
    try:
        output = fix_agent.invoke({"messages": [{"role": "user", "content": message}]}, context=context, config={"recursion_limit": MAX_STEPS})
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI fix failed: {e}")

    result = output["structured_response"]
    return result


def get_fixes(db: Session, user: User, repo: str):
    fixes = db.query(Fix).filter(Fix.user_id == user.id, Fix.repo == repo).order_by(Fix.id.desc()).all()
    return fixes


def approve_fix(db: Session, user: User, fix_id: int):
    fix = get_pending_fix(db, user, fix_id)
    token = get_token(user, fix.repo)
    pr = get_pr(token, fix.repo, fix.pr_number)

    branch = f"gitaudit/fix-pr{fix.pr_number}-{int(time.time())}"
    create_branch(token, fix.repo, branch, pr["head"]["sha"])
    files = {change["file"]: change["new_code"] for change in fix.changes}
    if fix.test_file:
        files[WORKFLOW_FILE] = make_workflow(fix.test_command)
    try:
        commit_files(token, fix.repo, branch, files, f"Fix: {fix.title}")
        new_pr = open_pr(token, fix.repo, f"Fix: {fix.title}", branch, pr["head"]["ref"],
                         f"AI fix for **{fix.title}** in `{fix.file}` (found in #{fix.pr_number}). Review it before merging.")
    except Exception:
        delete_branch(token, fix.repo, branch)
        raise

    fix.status = "approved"
    fix.pr_url = new_pr["html_url"]
    fix.branch = branch
    fix.ci_status = "running" if fix.test_file else "skipped"
    fix.attempts = 1
    db.commit()
    db.refresh(fix)
    return fix


def reject_fix(db: Session, user: User, fix_id: int):
    fix = get_pending_fix(db, user, fix_id)
    fix.status = "rejected"
    db.commit()
    db.refresh(fix)
    return fix


def check_tests(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.ci_status != "running":
        return fix
    token = get_token(user, fix.repo)

    run = latest_run(token, fix.repo, fix.branch)
    if run is None or run["status"] != "completed":
        return fix

    if run["conclusion"] == "success":
        fix.ci_status = "passed"
    elif fix.attempts >= MAX_ATTEMPTS:
        fix.ci_status = "failed"
    else:
        retry_fix(token, fix, test_log(token, fix.repo, run["id"]))
    db.commit()
    db.refresh(fix)
    return fix


def retry_fix(token: str, fix: Fix, log: str):
    context = Context(token=token, repo=fix.repo, ref=branch_sha(token, fix.repo, fix.branch))
    message = retry_prompt.format(
        title=fix.title,
        files=", ".join(change["file"] for change in fix.changes),
        test_file=fix.test_file,
        test_command=fix.test_command,
        log=log,
    )
    result = run_agent(message, context)

    changes = {change["file"]: change for change in fix.changes}
    for path, code in context.changes.items():
        if path in changes:
            changes[path] = {**changes[path], "new_code": code}
        else:
            changes[path] = {"file": path, "old_code": context.originals[path], "new_code": code}
    fix.changes = list(changes.values())
    fix.explanation = result.explanation
    test_file_ok = result.test_file in context.changes or result.test_file == fix.test_file
    if test_file_ok and result.test_command:
        fix.test_file = result.test_file
        fix.test_command = result.test_command
    fix.attempts += 1

    files = dict(context.changes)
    files[WORKFLOW_FILE] = make_workflow(fix.test_command)
    commit_files(token, fix.repo, fix.branch, files, f"Retry {fix.attempts}: {fix.title}")


def get_my_fix(db: Session, user: User, fix_id: int):
    fix = db.query(Fix).filter(Fix.id == fix_id, Fix.user_id == user.id).first()
    if fix is None:
        raise HTTPException(status_code=404, detail="Fix not found")
    return fix



def get_pending_fix(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.status != "pending":
        raise HTTPException(status_code=400, detail=f"This fix is already {fix.status}")
    return fix
