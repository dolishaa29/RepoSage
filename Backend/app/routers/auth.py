from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.user import LoginDto, RegisterDto, TokenResponse, UserResponse
from ..services import auth_service

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(data: RegisterDto, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginDto, db: Session = Depends(get_db)):
    token = auth_service.login(db, data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(auth)):
    return user
