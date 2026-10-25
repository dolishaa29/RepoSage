import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.github import GithubCodeDto, IndexResponse, PullResponse, RepoResponse
from ..schemas.user import TokenResponse, UserResponse
from ..services import github_service
from ..services.agent import code_index

router = APIRouter(prefix="/github", tags=["GitHub"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")


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


@router.get("/repos/{owner}/{name}/index", response_model=IndexResponse)
def index_status(owner: str, name: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    return IndexResponse(chunks=code_index.count_chunks(db, user, f"{owner}/{name}"))


@router.post("/repos/{owner}/{name}/index", response_model=IndexResponse)
def index_repo(owner: str, name: str, user: User = Depends(auth), db: Session = Depends(get_db)):
    return IndexResponse(chunks=code_index.index_repo(db, user, f"{owner}/{name}"))
