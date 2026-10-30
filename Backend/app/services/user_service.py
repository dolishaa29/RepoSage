import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.auth import create_token
from ..models.password_reset import PasswordReset
from ..models.user import User
from ..schemas.user import LoginDto, RegisterDto
from . import email_service

hasher = PasswordHasher()
RESET_TIME = timedelta(minutes=30)


def register(db: Session, data: RegisterDto):
    email = data.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hasher.hash(data.password)
    user = User(
        name=data.name,
        email=email,
        hashed_password=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, data: LoginDto):
    user = db.query(User).filter(func.lower(User.email) == data.email.lower()).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Wrong email or password")
    if user.hashed_password is None:
        raise HTTPException(status_code=401, detail="This account uses GitHub login")

    try:
        hasher.verify(user.hashed_password, data.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Wrong email or password")

    return create_token(user.id)


def hash_reset_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


# the answer is the same for every email, so nobody can check who has an account
def forgot_password(db: Session, email: str, background: BackgroundTasks):
    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="Password reset email is not set up yet")

    user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
    if user is None:
        return

    db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()
    token = secrets.token_urlsafe(32)
    db.add(PasswordReset(user_id=user.id, token_hash=hash_reset_token(token), expires_at=datetime.now(timezone.utc) + RESET_TIME))
    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
    text = f"Open this link to set a new gitAudit password. It works once, for 30 minutes.\n\n{frontend_url}/reset-password?token={token}\n\nIf you did not ask for this, ignore this email."
    background.add_task(email_service.send_email, user.email, "Reset your gitAudit password", text)


def reset_password(db: Session, token: str, password: str):
    reset = db.query(PasswordReset).filter(PasswordReset.token_hash == hash_reset_token(token)).first()
    if reset is None or reset.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This reset link is not valid. Ask for a new one")

    user = db.get(User, reset.user_id)
    user.hashed_password = hasher.hash(password)
    db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()
    db.commit()
