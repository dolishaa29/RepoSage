from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from ..core.db import Base

# one row = one AI fix for one finding. Saved so a fix survives a page refresh
# and we can follow it: pending → approved / rejected, then CI running → passed / failed.
class Fix(Base):
    __tablename__ = "fixes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    repo = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    file = Column(String, nullable=False)
    title = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    old_code = Column(Text, nullable=False)                    # kept to show old vs new side by side
    new_code = Column(Text, nullable=False)
    test_file = Column(String, nullable=False)                 # "" when the file cannot have a unit test (config, docs, ...)
    test_code = Column(Text, nullable=False)
    test_command = Column(Text, nullable=False, default="")    # what CI runs, e.g. "npm ci && npx jest tests/x.test.js"
    status = Column(String, nullable=False, default="pending")  # pending / approved / rejected (the person's decision)
    pr_url = Column(String, nullable=True)                     # set after approve
    branch = Column(String, nullable=True)                     # gitaudit/fix-..., needed to find its CI runs
    ci_status = Column(String, nullable=True)                  # running / passed / failed / skipped (the tests' result)
    attempts = Column(Integer, nullable=False, default=0)      # AI tries so far, stops at MAX_ATTEMPTS
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
