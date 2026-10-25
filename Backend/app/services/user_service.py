from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.auth import create_token
from ..models.user import User
from ..schemas.user import LoginDto, RegisterDto

hasher = PasswordHasher()


def register(db: Session, data: RegisterDto):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hasher.hash(data.password)
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, data: LoginDto):
    user = db.query(User).filter(User.email == data.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Wrong email or password")
    if user.hashed_password is None:
        raise HTTPException(status_code=401, detail="This account uses GitHub login")

    try:
        hasher.verify(user.hashed_password, data.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Wrong email or password")

    return create_token(user.id)
