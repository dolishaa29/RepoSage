from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # empty for users who signed up with GitHub

    github = relationship("GithubAccount", uselist=False, lazy="joined")

    @property
    def github_username(self):
        return self.github.username if self.github else None
