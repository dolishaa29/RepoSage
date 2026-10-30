from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import auth
from ..core.db import get_db
from ..models.user import User
from ..schemas.notification import NotificationResponse, UnreadCount
from ..services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(user: User = Depends(auth), db: Session = Depends(get_db)):
    return notification_service.get_notifications(db, user)


@router.get("/unread", response_model=UnreadCount)
def unread(user: User = Depends(auth), db: Session = Depends(get_db)):
    return UnreadCount(count=notification_service.count_unread(db, user))


@router.post("/read", response_model=UnreadCount)
def read_all(user: User = Depends(auth), db: Session = Depends(get_db)):
    notification_service.mark_all_read(db, user)
    return UnreadCount(count=0)
