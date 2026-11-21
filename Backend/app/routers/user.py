from fastapi import APIRouter, Depends

from ..core.auth import auth
from ..models.user import User
from ..schemas.user import UserResponse

router = APIRouter(tags=["User"])


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(auth)):
    return user
