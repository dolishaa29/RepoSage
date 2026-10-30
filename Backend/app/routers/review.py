from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.job import JobResponse
from ..schemas.review import ReviewDto, ReviewResponse
from ..services import job_service
from ..services.review import review_service

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", response_model=JobResponse)
def create_review(data: ReviewDto, background: BackgroundTasks, user: User = Depends(auth), db: Session = Depends(get_db)):
    def work(job_db: Session, job_user: User):
        review = review_service.review_pr(job_db, job_user, data.repo, data.pr_number)
        return ReviewResponse.model_validate(review).model_dump(mode="json")

    return job_service.start_job(db, user, background, "Review", data.repo, work)


@router.post("/reviews/{review_id}/publish-summary", response_model=ReviewResponse)
def publish_summary(review_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    return review_service.publish_summary(db, user, review_id)


@router.get("/reviews", response_model=list[ReviewResponse])
def list_reviews(repo: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    return review_service.get_reviews(db, user, repo)
