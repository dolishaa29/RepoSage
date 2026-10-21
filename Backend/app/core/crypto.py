import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

load_dotenv()

# Fernet = symmetric encryption from the cryptography library. The same key encrypts and decrypts.
# The key lives only in .env, so a leaked database alone does not give away users' GitHub tokens.
fernet = Fernet(os.getenv("TOKEN_ENCRYPTION_KEY"))


def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return fernet.decrypt(text.encode()).decode()


# A column type that encrypts on save and decrypts on load.
# The rest of the code just uses user.github_token as normal text and never has to remember to encrypt.
class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):  # Python → database
        if value is None:
            return None
        return encrypt(value)

    def process_result_value(self, value, dialect):  # database → Python
        if value is None:
            return None
        return decrypt(value)
