import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode

import httpx
from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.auth import SECRET_KEY, create_token
from ..core.crypto import decrypt, encrypt
from ..models.github_account import GithubAccount
from ..models.user import User

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8001/github/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")
SCOPE = "repo read:user user:email"


def authorize_url(mode: str, user_id: int | None = None) -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub login is not configured")

    # signed state: GitHub sends it back unchanged, so we know it came from us
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    state = jwt.encode({"mode": mode, "uid": user_id, "exp": expire}, SECRET_KEY)
    params = {"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "scope": SCOPE, "state": state}
    return "https://github.com/login/oauth/authorize?" + urlencode(params)


def _github_get(token: str, path: str, params: dict | None = None):
    res = httpx.get(
        "https://api.github.com" + path,
        params=params,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        timeout=10,
    )
    if res.status_code == 401:
        raise HTTPException(status_code=401, detail="GitHub access expired, connect GitHub again")
    res.raise_for_status()
    return res.json()


def _exchange_code(code: str) -> str:
    res = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code, "redirect_uri": REDIRECT_URI},
        headers={"Accept": "application/json"},
        timeout=10,
    )
    token = res.json().get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="GitHub login failed, please try again")
    return token


def _primary_email(token: str) -> str | None:
    for e in _github_get(token, "/user/emails"):
        if e["primary"] and e["verified"]:
            return e["email"].lower()
    return None


def _save_account(db: Session, user: User, gh: dict, token: str):
    account = db.query(GithubAccount).filter(GithubAccount.user_id == user.id).first()
    if account is None:
        account = GithubAccount(user_id=user.id)
        db.add(account)
    account.github_id = gh["id"]
    account.username = gh["login"]
    account.encrypted_token = encrypt(token)
    db.commit()


def _handle_callback(db: Session, code: str, state: dict) -> str:
    token = _exchange_code(code)
    gh = _github_get(token, "/user")
    linked = db.query(GithubAccount).filter(GithubAccount.github_id == gh["id"]).first()

    if state["mode"] == "connect":
        user = db.get(User, state["uid"])
        if user is None:
            raise HTTPException(status_code=400, detail="User not found")
        if linked and linked.user_id != user.id:
            raise HTTPException(status_code=400, detail="This GitHub account is linked to another user")
        _save_account(db, user, gh, token)
        return f"{FRONTEND_URL}/#/"

    # mode == "login": existing GitHub user, or create a new one
    if linked:
        user = db.get(User, linked.user_id)
    else:
        email = _primary_email(token)
        if email is None:
            raise HTTPException(status_code=400, detail="Your GitHub account has no verified email")
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Log in with your password and connect GitHub from the dashboard.",
            )
        user = User(name=gh.get("name") or gh["login"], email=email)
        db.add(user)
        db.flush()
    _save_account(db, user, gh, token)
    return f"{FRONTEND_URL}/#/github?token={create_token(user.id)}"


def callback(db: Session, code: str | None, state: str, error: str | None) -> str:
    """Returns the frontend URL to redirect the browser to."""
    try:
        if error or not code:
            raise HTTPException(status_code=400, detail="GitHub login was cancelled")
        try:
            data = jwt.decode(state, SECRET_KEY, algorithms=["HS256"])
        except JWTError:
            raise HTTPException(status_code=400, detail="GitHub login expired, please try again")
        return _handle_callback(db, code, data)
    except HTTPException as e:
        return f"{FRONTEND_URL}/#/?error={quote(str(e.detail))}"


def list_repos(user: User) -> list[dict]:
    if user.github is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    token = decrypt(user.github.encrypted_token)
    return _github_get(token, "/user/repos", {"per_page": 100, "sort": "updated"})
