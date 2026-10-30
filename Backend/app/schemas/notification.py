from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kind: str
    message: str
    link: str
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    count: int
