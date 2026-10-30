from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from ..core.db import Base

class SeenItem(Base):
    __tablename__ = "seen_items"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_seen_items_user_key"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, nullable=False)
