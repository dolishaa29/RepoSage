from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..core.db import get_db
from ..models.user import User
from ..dto.auth_dto import LoginDto, RegisterDto
from ..schemas.user import TokenResponse, UserResponse
from ..services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(data: RegisterDto, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginDto, db: Session = Depends(get_db)):
    token = auth_service.login(db, data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
