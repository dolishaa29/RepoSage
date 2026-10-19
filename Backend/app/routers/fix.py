from fastapi import APIRouter, Depends

from ..core.auth import auth
from ..models.user import User
from ..schemas.fix import ApplyFixDto, ApplyFixResponse, FixDto, FixResponse
from ..services import fix_service

router = APIRouter(prefix="/fixes", tags=["Fixes"])


@router.post("", response_model=FixResponse)
def create_fix(data: FixDto, user: User = Depends(auth)):
    return fix_service.make_fix(user, data.repo, data.pr_number, data.finding)


@router.post("/apply", response_model=ApplyFixResponse)
def apply_fix(data: ApplyFixDto, user: User = Depends(auth)):
    return fix_service.apply_fix(user, data.repo, data.pr_number, data.file, data.new_code, data.title)
