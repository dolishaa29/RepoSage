from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from ..core.db import Base

class Fix(Base):
    __tablename__ = "fixes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    repo = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    file = Column(String, nullable=False)
    title = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    changes = Column(JSON, nullable=False)
    test_file = Column(String, nullable=False)
    test_command = Column(Text, nullable=False, default="")    
    status = Column(String, nullable=False, default="pending") 
    pr_url = Column(String, nullable=True)                     
    branch = Column(String, nullable=True)                     
    ci_status = Column(String, nullable=True)                  
    attempts = Column(Integer, nullable=False, default=0)      
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
