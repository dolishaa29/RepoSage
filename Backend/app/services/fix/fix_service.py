import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...models.fix import Fix
from ...models.user import User
from ...schemas.review import Finding
from .github_files import create_branch, get_pr, latest_run, open_pr, read_file, save_file, test_log
from .prompts import chain, retry_chain
from .workflow import WORKFLOW_FILE, make_workflow

# Flow: make_fix → person approves or rejects → approve opens a PR → GitHub Actions runs the test
#       → check_tests: passed / failed / AI tries again (max 3).
# Tests run on GitHub, never on our server: running code from someone's repo here would be unsafe.

MAX_ATTEMPTS = 3


# POST /fixes: AI writes the fix + test. Saved as "pending", nothing is sent to GitHub yet.
def make_fix(db: Session, user: User, repo: str, pr_number: int, finding: Finding):
    token = get_token(user)
    pr = get_pr(token, repo, pr_number)
    code = read_file(token, repo, finding.file, pr["head"]["ref"])

    try:
        result = chain.invoke({
            "title": finding.title,
            "line": finding.line,
            "explanation": finding.explanation,
            "suggestion": finding.suggestion,
            "file": finding.file,
            "code": code,
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI fix failed: {e}")

    fix = Fix(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        file=finding.file,
        title=finding.title,
        explanation=result.explanation,
        old_code=code,
        new_code=result.fixed_code,
        test_file=result.test_file,
        test_code=result.test_code,
        test_command=result.test_command,
    )
    db.add(fix)
    db.commit()
    db.refresh(fix)
    return fix


def get_fixes(db: Session, user: User, repo: str):
    return db.query(Fix).filter(Fix.user_id == user.id, Fix.repo == repo).order_by(Fix.id.desc()).all()


# POST /fixes/{id}/approve: new branch → commit fix, test, workflow → PR into the original PR's branch.
# The workflow is committed last, so CI runs once, when code and test are already there.
def approve_fix(db: Session, user: User, fix_id: int):
    fix = get_pending_fix(db, user, fix_id)
    token = get_token(user)
    pr = get_pr(token, fix.repo, fix.pr_number)

    branch = f"gitaudit/fix-pr{fix.pr_number}-{int(time.time())}"
    create_branch(token, fix.repo, branch, pr["head"]["sha"])
    save_file(token, fix.repo, fix.file, fix.new_code, branch, f"Fix: {fix.title}")
    if fix.test_file:
        save_file(token, fix.repo, fix.test_file, fix.test_code, branch, f"Test: {fix.title}")
        save_file(token, fix.repo, WORKFLOW_FILE, make_workflow(fix.test_command), branch, "Run gitAudit tests")

    new_pr = open_pr(token, fix.repo, f"Fix: {fix.title}", branch, pr["head"]["ref"],
                     f"AI fix for **{fix.title}** in `{fix.file}` (found in #{fix.pr_number}). Review it before merging.")

    fix.status = "approved"
    fix.pr_url = new_pr["html_url"]
    fix.branch = branch
    fix.ci_status = "running" if fix.test_file else "skipped"
    fix.attempts = 1
    db.commit()
    db.refresh(fix)
    return fix


# POST /fixes/{id}/reject: nothing was sent to GitHub, so we only mark it
def reject_fix(db: Session, user: User, fix_id: int):
    fix = get_pending_fix(db, user, fix_id)
    fix.status = "rejected"
    db.commit()
    db.refresh(fix)
    return fix


# POST /fixes/{id}/check: read the CI result. Failed → the AI gets the error and tries again on the same branch.
def check_tests(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.ci_status != "running":
        return fix
    token = get_token(user)

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


# new code + test + command on the SAME branch, so the open PR updates and CI runs again
def retry_fix(token: str, fix: Fix, log: str):
    try:
        result = retry_chain.invoke({
            "title": fix.title,
            "file": fix.file,
            "code": fix.new_code,
            "test_file": fix.test_file,
            "test_code": fix.test_code,
            "test_command": fix.test_command,
            "log": log,
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI retry failed: {e}")

    fix.new_code = result.fixed_code
    fix.test_code = result.test_code
    fix.test_command = result.test_command
    fix.explanation = result.explanation
    fix.attempts += 1
    save_file(token, fix.repo, fix.file, fix.new_code, fix.branch, f"Retry {fix.attempts}: {fix.title}")
    save_file(token, fix.repo, fix.test_file, fix.test_code, fix.branch, f"Retry {fix.attempts}: test")
    save_file(token, fix.repo, WORKFLOW_FILE, make_workflow(fix.test_command), fix.branch, f"Retry {fix.attempts}: test command")


# the fix must belong to this user, so nobody can approve someone else's fix by guessing an id
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


def get_token(user: User):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    return user.github_token
