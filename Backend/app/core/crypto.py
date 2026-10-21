import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

load_dotenv()

fernet = Fernet(os.getenv("TOKEN_ENCRYPTION_KEY"))


def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return fernet.decrypt(text.encode()).decode()


class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt(value)
