from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.crypto import decrypt
from ..core.llm import get_llm
from ..models.review import Review
from ..models.user import User
from ..schemas.review import ReviewResult
from .github_service import call_github

MAX_DIFF_CHARS = 200_000

PROMPT = """You are a senior software engineer and security auditor reviewing a GitHub pull request.

Look only at the changes in the diff below and report real problems:
- bugs: wrong logic, crashes, missing error handling
- security issues: SQL injection, hardcoded secrets, broken authentication, unsafe handling of user input
- bad practices that will cause problems later

For each problem give the file, the line number in the new code (if you can tell), how serious it is,
why it is a problem, and how to fix it. Skip style nitpicks.
If the changes look fine, return an empty findings list.

Pull request title: {title}

Diff:
{diff}"""


def review_pr(db: Session, user: User, repo: str, pr_number: int) -> Review:
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    token = decrypt(user.github_token)

    # 1. get the pull request and its changed code from GitHub
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    files = call_github(token, f"/repos/{repo}/pulls/{pr_number}/files")
    diff = make_diff(files)
    if not diff:
        raise HTTPException(status_code=400, detail="This pull request has no code changes to review")
    if len(diff) > MAX_DIFF_CHARS:
        raise HTTPException(status_code=400, detail="This pull request is too big to review")

    # 2. ask Claude, and get the answer back as a ReviewResult object
    reviewer = get_llm().with_structured_output(ReviewResult, method="json_schema")
    try:
        result = reviewer.invoke(PROMPT.format(title=pr["title"], diff=diff))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI review failed: {e}")

    # 3. save it
    review = Review(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        pr_title=pr["title"],
        summary=result.summary,
        findings=[f.model_dump() for f in result.findings],
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, user: User, repo: str) -> list[Review]:
    return (
        db.query(Review)
        .filter(Review.user_id == user.id, Review.repo == repo)
        .order_by(Review.id.desc())
        .all()
    )


# turns GitHub's list of changed files into one text diff
def make_diff(files: list[dict]) -> str:
    parts = []
    for f in files:
        if f.get("patch"):  # binary files have no patch
            parts.append(f"### {f['filename']}\n{f['patch']}")
    return "\n\n".join(parts)
