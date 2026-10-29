from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...models.review import Review
from ...models.user import User
from ..agent.tools import Context
from ..github_service import call_github, get_token
from .graph import review_graph

SKIP_FILES = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock", "go.sum",
              ".min.js", ".min.css", ".map", ".svg")
CHUNK_SIZE = 30000
MAX_CHUNKS = 6


def review_pr(db: Session, user: User, repo: str, pr_number: int):
    token = get_token(user, repo)
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    files = call_github(token, f"/repos/{repo}/pulls/{pr_number}/files?per_page=100")
    chunks, skipped = make_chunks(files)
    if len(chunks) == 0:
        raise HTTPException(status_code=400, detail="This pull request has no code changes to review")

    context = Context(token=token, repo=repo, ref=pr["head"]["sha"])
    try:
        state = review_graph.invoke({
            "title": pr["title"],
            "files": "\n".join(f"{f['filename']} (+{f['additions']} -{f['deletions']})" for f in files),
            "chunks": chunks,
            "skipped": skipped,
            "structure": [],
            "security": [],
        }, context=context)
        result = state["result"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI review failed: {e}")

    review = Review(
        user_id=user.id,
        repo=repo,
        pr_number=pr_number,
        pr_title=pr["title"],
        ai="gemini · langgraph agents",
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
    reviews = reviews.order_by(Review.id.desc()).all()
    return reviews


def make_chunks(files):
    skipped = []
    pieces = []
    for file in files:
        name = file["filename"]
        if "patch" not in file or name.endswith(SKIP_FILES):
            skipped.append(name)
            continue
        for part in pack(file["patch"].splitlines(keepends=True)):
            pieces.append("### " + name + "\n" + part + "\n\n")

    chunks = pack(pieces)

    for extra in chunks[MAX_CHUNKS:]:
        for line in extra.splitlines():
            if line.startswith("### "):
                skipped.append(line[4:])
    return chunks[:MAX_CHUNKS], sorted(set(skipped))


def pack(texts):
    groups = []
    group = ""
    for text in texts:
        if group != "" and len(group) + len(text) > CHUNK_SIZE:
            groups.append(group)
            group = ""
        group = group + text
    if group != "":
        groups.append(group)
    return groups
