from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from ..core.db import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)
    status = Column(String, nullable=False, default="running")
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
