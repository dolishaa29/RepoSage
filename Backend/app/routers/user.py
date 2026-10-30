from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.user import ForgotPasswordDto, LoginDto, RegisterDto, ResetPasswordDto, TokenResponse, UserResponse
from ..services import user_service

router = APIRouter(tags=["User"])


@router.post("/register", response_model=UserResponse)
def register(data: RegisterDto, db: Session = Depends(get_db)):
    return user_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginDto, db: Session = Depends(get_db)):
    token = user_service.login(db, data)
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordDto, background: BackgroundTasks, db: Session = Depends(get_db)):
    user_service.forgot_password(db, data.email, background)
    return {"ok": True}


@router.post("/reset-password")
def reset_password(data: ResetPasswordDto, db: Session = Depends(get_db)):
    user_service.reset_password(db, data.token, data.password)
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(auth)):
    return user
