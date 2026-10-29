from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from ..core.db import Base
from .github_account import GithubAccount

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    github_accounts = relationship(GithubAccount, order_by=GithubAccount.id)
