from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session

from ..core.llm import model
from ..models.review import Review
from ..models.user import User
from ..schemas.review import ReviewResult
from .github_service import call_github

prompt = PromptTemplate(
    template="""You are a senior software engineer and security auditor reviewing a GitHub pull request.

Look only at the changes in the diff below and report real problems:
- bugs: wrong logic, crashes, missing error handling
- security issues: SQL injection, hardcoded secrets, broken authentication, unsafe handling of user input
- bad practices that will cause problems later

For each problem give the file, the line number, how serious it is, why it is a problem, and how to fix it.
Skip style nitpicks. If the changes look fine, return an empty findings list.

Pull request title: {title}

Diff:
{diff}""",
    input_variables=["title", "diff"],
)

structured_model = model.with_structured_output(ReviewResult)
chain = prompt | structured_model


def review_pr(db: Session, user: User, repo: str, pr_number: int):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")

    pr = call_github(user.github_token, f"/repos/{repo}/pulls/{pr_number}")
    files = call_github(user.github_token, f"/repos/{repo}/pulls/{pr_number}/files")
    diff = make_diff(files)
    if diff == "":
        raise HTTPException(status_code=400, detail="This pull request has no code changes to review")

    # 2. ask Gemini
    try:
        result = chain.invoke({"title": pr["title"], "diff": diff})
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI review failed: {e}")

    # 3. save it
    review = Review(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        pr_title=pr["title"],
        ai="gemini",
        summary=result.summary,
        findings=[f.model_dump() for f in result.findings],
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, user: User, repo: str):
    return db.query(Review).filter(Review.user_id == user.id, Review.repo == repo).order_by(Review.id.desc()).all()


# GitHub gives a list of changed files; join them into one text for the AI
def make_diff(files):
    diff = ""
    for f in files:
        if "patch" in f:  # images and other binary files have no patch
            diff += f"### {f['filename']}\n{f['patch']}\n\n"
    return diff
