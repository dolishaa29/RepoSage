from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from ..core.db import Base

class GithubAccount(Base):
    __tablename__ = "github_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    github_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    encrypted_token = Column(String, nullable=False)
