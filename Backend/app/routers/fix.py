from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.fix import FixDto, FixResponse
from ..schemas.job import JobResponse
from ..services import job_service
from ..services.fix import fix_service

router = APIRouter(prefix="/fixes", tags=["Fixes"])


@router.post("", response_model=JobResponse)
def create_fix(data: FixDto, background: BackgroundTasks, user: User = Depends(auth), db: Session = Depends(get_db)):
    def work(job_db: Session, job_user: User):
        fix = fix_service.make_fix(job_db, job_user, data.repo, data.pr_number, data.finding)
        return FixResponse.model_validate(fix).model_dump(mode="json")

    return job_service.start_job(db, user, background, "Fix", data.repo, work)


@router.get("", response_model=list[FixResponse])
def list_fixes(repo: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    return fix_service.get_fixes(db, user, repo)


@router.post("/{fix_id}/approve", response_model=FixResponse)
def approve_fix(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    return fix_service.approve_fix(db, user, fix_id)


@router.post("/{fix_id}/check", response_model=FixResponse)
def check_tests(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    return fix_service.check_tests(db, user, fix_id)


@router.post("/{fix_id}/reject", response_model=FixResponse)
def reject_fix(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    return fix_service.reject_fix(db, user, fix_id)
