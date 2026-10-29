from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.stats import StatsResponse
from ..services import stats_service

router = APIRouter(tags=["Stats"])


@router.get("/stats", response_model=StatsResponse)
def stats(user: User = Depends(auth), db: Session = Depends(get_db)):
    return stats_service.get_stats(db, user)
