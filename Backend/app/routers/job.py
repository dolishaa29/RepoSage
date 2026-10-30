from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.job import JobResponse
from ..services import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    return job_service.get_job(db, user, job_id)
