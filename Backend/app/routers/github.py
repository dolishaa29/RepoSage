import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.github import GithubCodeDto, PullResponse, RepoResponse
from ..schemas.user import TokenResponse, UserResponse
from ..services import github_service

router = APIRouter(prefix="/github", tags=["GitHub"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")


# If the GitHub OAuth App's callback URL is http://localhost:8001/github/callback,
# GitHub sends the user here. We just pass ?code=...&state=... on to the frontend.
@router.get("/callback")
def callback(request: Request):
    return RedirectResponse(f"{FRONTEND_URL}/?{request.url.query}")


@router.post("/login", response_model=TokenResponse)
def github_login(data: GithubCodeDto, db: Session = Depends(get_db)):
    token = github_service.login(db, data.code)
    return TokenResponse(access_token=token)


@router.post("/connect", response_model=UserResponse)
def github_connect(data: GithubCodeDto, user: User = Depends(auth), db: Session = Depends(get_db)):
    return github_service.connect(db, user, data.code)


@router.get("/repos", response_model=list[RepoResponse])
def repos(user: User = Depends(auth)):
    return github_service.get_repos(user)


@router.get("/repos/{owner}/{name}/pulls", response_model=list[PullResponse])
def pulls(owner: str, name: str, user: User = Depends(auth)):
    return github_service.get_pulls(user, f"{owner}/{name}")
