from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.auth import create_token
from ..models.user import User
from ..schemas.user import LoginDto, RegisterDto

hasher = PasswordHasher()


def register(db: Session, data: RegisterDto):
    print("registering", data.name, data.email)
    if db.query(User).filter(User.email == data.email).first():
        print("email exists", data.email)
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hasher.hash(data.password)
    print("hashed", hashed)
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("user saved", user.id)
    return user


def login(db: Session, data: LoginDto):
    print("logging in", data.email)
    user = db.query(User).filter(User.email == data.email).first()
    if user is None:
        print("no user", data.email)
        raise HTTPException(status_code=401, detail="Wrong email or password")
    if user.hashed_password is None:
        print("github only", user.id)
        raise HTTPException(status_code=401, detail="This account uses GitHub login")

    try:
        hasher.verify(user.hashed_password, data.password)
    except VerifyMismatchError:
        print("wrong password", user.id)
        raise HTTPException(status_code=401, detail="Wrong email or password")

    print("login ok", user.id)
    return create_token(user.id)
