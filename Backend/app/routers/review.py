from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.review import ReviewDto, ReviewResponse
from ..services.review import review_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse)
def create_review(data: ReviewDto, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("review hit", data.repo, data.pr_number)
    return review_service.review_pr(db, user, data.repo, data.pr_number)


@router.get("", response_model=list[ReviewResponse])
def list_reviews(repo: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("reviews list", repo)
    return review_service.get_reviews(db, user, repo)
