from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.github import RepoResponse, UrlResponse
from ..services import github_service

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.get("/login-url", response_model=UrlResponse)
def login_url():
    return UrlResponse(url=github_service.authorize_url("login"))


@router.get("/connect-url", response_model=UrlResponse)
def connect_url(user: User = Depends(auth)):
    return UrlResponse(url=github_service.authorize_url("connect", user.id))


@router.get("/callback")
def callback(code: str | None = None, state: str = "", error: str | None = None, db: Session = Depends(get_db)):
    return RedirectResponse(github_service.callback(db, code, state, error))


@router.get("/repos", response_model=list[RepoResponse])
def repos(user: User = Depends(auth)):
    return github_service.list_repos(user)
