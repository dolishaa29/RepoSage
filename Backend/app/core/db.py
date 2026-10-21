import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1
)

# Neon has IPv6 and IPv4 addresses, but IPv6 does not work on this machine.
# Without help, every new connection first waits for IPv6 to time out (~14s).
# hostaddr = the IPv4 address, so we connect over IPv4 straight away (~2s).
# The hostname is still sent, because Neon uses it to find the right database.
DB_IPV4 = socket.gethostbyname(urlparse(DATABASE_URL).hostname)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # check a connection is alive before using it
    pool_recycle=240,       # Neon silently closes idle connections; replace ours every 4 min so a request never waits on a dead one
    # 10s: enough for a sleeping Neon database (free tier) to wake up
    connect_args={"connect_timeout": 10, "hostaddr": DB_IPV4},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()