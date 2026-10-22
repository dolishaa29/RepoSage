import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..models.user import User
from .db import get_db


SECRET_KEY = os.getenv("JWT")
print("jwt secret found", bool(SECRET_KEY))

bearer = HTTPBearer()


def create_token(user_id: int):
    print("creating token", user_id)
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"sub": str(user_id), "exp": expire}
    print("payload", payload)
    token = jwt.encode(payload, SECRET_KEY)
    print("token", token)
    return token


def auth( creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    print("checking token", creds.credentials)
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
        print("payload", payload)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as e:
        print("bad token", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, user_id)
    if user is None:
        print("user missing", user_id)
        raise HTTPException(status_code=401, detail="User not found")
    print("user found", user.id, user.email)
    return user
