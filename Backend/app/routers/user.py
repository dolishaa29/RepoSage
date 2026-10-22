from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.user import LoginDto, RegisterDto, TokenResponse, UserResponse
from ..services import user_service

router = APIRouter(tags=["User"])


@router.post("/register", response_model=UserResponse)
def register(data: RegisterDto, db: Session = Depends(get_db)):
    print("register hit", data.email)
    return user_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginDto, db: Session = Depends(get_db)):
    print("login hit", data.email)
    token = user_service.login(db, data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(auth)):
    print("me hit", user.id)
    return user
