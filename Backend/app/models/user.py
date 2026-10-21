from sqlalchemy import BigInteger, Column, DateTime, Integer, String, func
from ..core.crypto import EncryptedString
from ..core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  
    github_id = Column(BigInteger, unique=True, nullable=True)
    github_username = Column(String, nullable=True)
    github_token = Column(EncryptedString, nullable=True)  # stored encrypted, read back as plain text (core/crypto.py)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
