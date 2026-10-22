from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.fix import FixDto, FixResponse
from ..services.fix import fix_service

router = APIRouter(prefix="/fixes", tags=["Fixes"])


@router.post("", response_model=FixResponse)
def create_fix(data: FixDto, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("fix hit", data.repo, data.pr_number, data.finding)
    return fix_service.make_fix(db, user, data.repo, data.pr_number, data.finding)


@router.get("", response_model=list[FixResponse])
def list_fixes(repo: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("fixes list", repo)
    return fix_service.get_fixes(db, user, repo)


@router.post("/{fix_id}/approve", response_model=FixResponse)
def approve_fix(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("approve hit", fix_id)
    return fix_service.approve_fix(db, user, fix_id)


@router.post("/{fix_id}/check", response_model=FixResponse)
def check_tests(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("check hit", fix_id)
    return fix_service.check_tests(db, user, fix_id)


@router.post("/{fix_id}/reject", response_model=FixResponse)
def reject_fix(fix_id: int, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("reject hit", fix_id)
    return fix_service.reject_fix(db, user, fix_id)
