from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from ..core.crypto import EncryptedString
from ..core.db import Base

class GithubAccount(Base):
    __tablename__ = "github_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    github_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    token = Column("encrypted_token", EncryptedString, nullable=False)
