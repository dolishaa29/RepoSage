import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("db url found", bool(DATABASE_URL))

DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1
)

DB_IPV4 = socket.gethostbyname(urlparse(DATABASE_URL).hostname)
print("db ip", DB_IPV4)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=240,
    connect_args={"connect_timeout": 10, "hostaddr": DB_IPV4},
)
print("engine ready")

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    print("db open")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        print("db closed")
