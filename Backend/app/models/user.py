from sqlalchemy import BigInteger, Column, Integer, String
from ..core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # empty for users who signed up with GitHub

    # filled when the user logs in with / connects GitHub
    github_id = Column(BigInteger, unique=True, nullable=True)
    github_username = Column(String, nullable=True)
    github_token = Column(String, nullable=True)  # encrypted
