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
print("frontend url", FRONTEND_URL)


@router.get("/callback")
def callback(request: Request):
    print("callback hit", request.url.query)
    return RedirectResponse(f"{FRONTEND_URL}/?{request.url.query}")


@router.post("/login", response_model=TokenResponse)
def github_login(data: GithubCodeDto, db: Session = Depends(get_db)):
    print("github login", data.code)
    token = github_service.login(db, data.code)
    return TokenResponse(access_token=token)


@router.post("/connect", response_model=UserResponse)
def github_connect(data: GithubCodeDto, user: User = Depends(auth), db: Session = Depends(get_db)):
    print("github connect", user.id, data.code)
    return github_service.connect(db, user, data.code)


@router.get("/repos", response_model=list[RepoResponse])
def repos(user: User = Depends(auth)):
    print("repos hit", user.id)
    return github_service.get_repos(user)


@router.get("/repos/{owner}/{name}/pulls", response_model=list[PullResponse])
def pulls(owner: str, name: str, user: User = Depends(auth)):
    print("pulls hit", owner, name)
    return github_service.get_pulls(user, f"{owner}/{name}")
