from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...models.review import Review
from ...models.user import User
from ...schemas.review import Finding
from ..github_service import call_github
from .prompts import RULES, lead_chain, parallel_chain


def review_pr(db: Session, user: User, repo: str, pr_number: int):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")

    pr = call_github(user.github_token, f"/repos/{repo}/pulls/{pr_number}")
    files = call_github(user.github_token, f"/repos/{repo}/pulls/{pr_number}/files")
    diff = make_diff(files)
    if diff == "":
        raise HTTPException(status_code=400, detail="This pull request has no code changes to review")

    try:
        agents = parallel_chain.invoke({"rules": RULES, "title": pr["title"], "diff": diff})
        result = lead_chain.invoke({
            "structure_findings": to_text(agents["structure"].findings),
            "security_findings": to_text(agents["security"].findings),
            "title": pr["title"],
            "diff": diff,
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI review failed: {e}")

    review = Review(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        pr_title=pr["title"],
        ai="gemini · 3 agents",
        summary=result.summary,
        findings=[f.model_dump() for f in result.findings],
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, user: User, repo: str):
    reviews = db.query(Review)
    reviews = reviews.filter(Review.user_id == user.id)
    reviews = reviews.filter(Review.repo == repo)
    return reviews.order_by(Review.id.desc()).all()


def make_diff(files):
    diff = ""
    for file in files:
        if "patch" in file:
            name = file["filename"]
            code = file["patch"]
            diff = diff + "### " + name + "\n" + code + "\n\n"
    return diff


def to_text(findings: list[Finding]):
    text = ""
    for f in findings:
        text = text + f"- [{f.severity}] [{f.category}] {f.file}:{f.line} {f.title}. {f.explanation} Fix: {f.suggestion}\n"
    if text == "":
        text = "nothing"
    return text
