import base64
import os
import time

from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session

from ..core.llm import model
from ..models.fix import Fix
from ..models.user import User
from ..schemas.fix import FixResult
from ..schemas.review import Finding
from .github_service import call_github, find_file_sha, get_github_text, send_github

MAX_ATTEMPTS = 3
WORKFLOW_FILE = ".github/workflows/gitaudit-tests.yml"
WORKFLOW = """name: gitAudit tests
on:
  push:
    branches: ["gitaudit/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: |
          for f in $(find . -name requirements.txt -not -path "*/node_modules/*"); do pip install -r "$f" || true; done
          pip install pytest
      - run: python -m pytest tests/gitaudit -q
"""

TEST_RULES = """Also write a pytest file that checks the fix. It will be saved at {test_file}.
The tests run from the repository root with: python -m pytest tests/gitaudit
To import the code, add the file's folder to sys.path first (for example sys.path.insert(0, "Backend")).
Do not use the network or a real database in the test."""

NO_TEST_RULES = "Return an empty test_code."

prompt = PromptTemplate(
    template="""You are a senior software engineer. Fix only this one problem in the file below.

Problem: {title}
Line: {line}
Why it is a problem: {explanation}
How to fix it: {suggestion}

Change only what is needed for this problem and keep everything else exactly the same.
Return the complete fixed file.

{test_rules}

File: {file}
{code}""",
    input_variables=["title", "line", "explanation", "suggestion", "test_rules", "file", "code"],
)

retry_prompt = PromptTemplate(
    template="""You are a senior software engineer. Your fix for "{title}" failed its tests.

File: {file}
{code}

Test file: {test_file}
{test_code}

Test output:
{log}

Fix the code or the test so the tests pass. The fix for "{title}" must stay in place.
Return the complete file and the complete test file.""",
    input_variables=["title", "file", "code", "test_file", "test_code", "log"],
)

structured_model = model.with_structured_output(FixResult)
chain = prompt | structured_model
retry_chain = retry_prompt | structured_model


def make_fix(db: Session, user: User, repo: str, pr_number: int, finding: Finding):
    token = get_token(user)
    pr = get_pr(token, repo, pr_number)
    code = read_file(token, repo, finding.file, pr["head"]["ref"])
    test_file = make_test_path(finding.file)

    try:
        result = chain.invoke({
            "title": finding.title,
            "line": finding.line,
            "explanation": finding.explanation,
            "suggestion": finding.suggestion,
            "test_rules": TEST_RULES.format(test_file=test_file) if test_file else NO_TEST_RULES,
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
        test_file=test_file,
        test_code=result.test_code if test_file else "",
    )

    db.add(fix)
    db.commit()
    db.refresh(fix)
    return fix


def get_fixes(db: Session, user: User, repo: str):
    return db.query(Fix).filter(Fix.user_id == user.id, Fix.repo == repo).order_by(Fix.id.desc()).all()


def approve_fix(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.status != "pending":
        raise HTTPException(status_code=400, detail=f"This fix is already {fix.status}")
    token = get_token(user)
    pr = get_pr(token, fix.repo, fix.pr_number)
    pr_branch = pr["head"]["ref"]

    new_branch = f"gitaudit/fix-pr{fix.pr_number}-{int(time.time())}"
    send_github(token, "POST", f"/repos/{fix.repo}/git/refs", {
        "ref": f"refs/heads/{new_branch}",
        "sha": pr["head"]["sha"],
    })
    save_file(token, fix.repo, fix.file, fix.new_code, new_branch, f"Fix: {fix.title}")
    if fix.test_file:
        save_file(token, fix.repo, fix.test_file, fix.test_code, new_branch, f"Test: {fix.title}")
        save_file(token, fix.repo, WORKFLOW_FILE, WORKFLOW, new_branch, "Run gitAudit tests")

    new_pr = send_github(token, "POST", f"/repos/{fix.repo}/pulls", {
        "title": f"Fix: {fix.title}",
        "head": new_branch,
        "base": pr_branch,
        "body": f"AI fix for **{fix.title}** in `{fix.file}`, found while reviewing #{fix.pr_number}.\n\n"
                f"Unit test: `{fix.test_file or 'none'}`.\n\nReview it before merging.",
    })

    fix.status = "approved"
    fix.pr_url = new_pr["html_url"]
    fix.branch = new_branch
    fix.ci_status = "running" if fix.test_file else "skipped"
    fix.attempts = 1
    db.commit()
    db.refresh(fix)
    return fix


def reject_fix(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.status != "pending":
        raise HTTPException(status_code=400, detail=f"This fix is already {fix.status}")
    fix.status = "rejected"
    db.commit()
    db.refresh(fix)
    return fix


def check_tests(db: Session, user: User, fix_id: int):
    fix = get_my_fix(db, user, fix_id)
    if fix.ci_status != "running":
        return fix
    token = get_token(user)

    head_sha = call_github(token, f"/repos/{fix.repo}/branches/{fix.branch}")["commit"]["sha"]
    runs = call_github(token, f"/repos/{fix.repo}/actions/runs?branch={fix.branch}&head_sha={head_sha}")["workflow_runs"]
    if not runs or runs[0]["status"] != "completed":
        return fix

    if runs[0]["conclusion"] == "success":
        fix.ci_status = "passed"
    elif fix.attempts >= MAX_ATTEMPTS:
        fix.ci_status = "failed"
    else:
        retry_fix(token, fix, get_test_log(token, fix.repo, runs[0]["id"]))
    db.commit()
    db.refresh(fix)
    return fix


def retry_fix(token: str, fix: Fix, log: str):
    try:
        result = retry_chain.invoke({
            "title": fix.title,
            "file": fix.file,
            "code": fix.new_code,
            "test_file": fix.test_file,
            "test_code": fix.test_code,
            "log": log,
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI retry failed: {e}")

    fix.new_code = result.fixed_code
    fix.test_code = result.test_code
    fix.explanation = result.explanation
    fix.attempts += 1
    save_file(token, fix.repo, fix.file, fix.new_code, fix.branch, f"Retry {fix.attempts}: {fix.title}")
    save_file(token, fix.repo, fix.test_file, fix.test_code, fix.branch, f"Retry {fix.attempts}: test for {fix.title}")


def get_test_log(token: str, repo: str, run_id: int):
    jobs = call_github(token, f"/repos/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    log = get_github_text(token, f"/repos/{repo}/actions/jobs/{jobs[0]['id']}/logs")
    return log[-4000:]


def make_test_path(file: str):
    if not file.endswith(".py"):
        return ""
    name = os.path.splitext(os.path.basename(file))[0]
    return f"tests/gitaudit/test_{name}.py"


def get_my_fix(db: Session, user: User, fix_id: int):
    fix = db.query(Fix).filter(Fix.id == fix_id, Fix.user_id == user.id).first()
    if fix is None:
        raise HTTPException(status_code=404, detail="Fix not found")
    return fix


def get_token(user: User):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    return user.github_token


def get_pr(token: str, repo: str, pr_number: int):
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr


def read_file(token: str, repo: str, path: str, branch: str):
    data = call_github(token, f"/repos/{repo}/contents/{path}?ref={branch}")
    return base64.b64decode(data["content"]).decode()


def save_file(token: str, repo: str, path: str, code: str, branch: str, message: str):
    body = {
        "message": message,
        "content": base64.b64encode(code.encode()).decode(),
        "branch": branch,
    }
    sha = find_file_sha(token, repo, path, branch)
    if sha:
        body["sha"] = sha
    send_github(token, "PUT", f"/repos/{repo}/contents/{path}", body)
