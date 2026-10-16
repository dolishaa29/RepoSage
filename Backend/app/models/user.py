from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str]  
