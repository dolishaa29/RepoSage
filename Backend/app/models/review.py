from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from ..core.db import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    repo = Column(String, nullable=False)          # "owner/name"
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    findings = Column(JSON, nullable=False)        # list of problems the AI found
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
