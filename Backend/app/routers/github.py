from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..dto.github_dto import GithubCodeDto
from ..models.user import User
from ..schemas.github import RepoResponse
from ..schemas.user import TokenResponse, UserResponse
from ..services import github_service

router = APIRouter(prefix="/github", tags=["GitHub"])


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
