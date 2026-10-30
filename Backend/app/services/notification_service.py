from sqlalchemy.orm import Session

from ..models.notification import Notification
from ..models.user import User

MAX_SHOWN = 50


def add_notification(db: Session, user_id: int, kind: str, message: str, repo: str):
    notification = Notification(user_id=user_id, kind=kind, message=message, link=f"/repo/{repo}")
    db.add(notification)


def get_notifications(db: Session, user: User):
    notifications = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.id.desc()).limit(MAX_SHOWN).all()
    return notifications


def count_unread(db: Session, user: User):
    count = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
    return count


def mark_all_read(db: Session, user: User):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
