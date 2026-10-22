import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

load_dotenv()

key = os.getenv("TOKEN_ENCRYPTION_KEY")
print("key found", bool(key))
fernet = Fernet(key)
print("fernet ready")


def encrypt(text: str) -> str:
    print("encrypting", text)
    result = fernet.encrypt(text.encode()).decode()
    print("encrypted", result)
    return result


def decrypt(text: str) -> str:
    print("decrypting", text)
    try:
        result = fernet.decrypt(text.encode()).decode()
    except Exception as e:
        print("decrypt failed", type(e).__name__)
        raise
    print("decrypted", result)
    return result


class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        print("saving", value)
        if value is None:
            return None
        return encrypt(value)

    def process_result_value(self, value, dialect):
        print("loading", value)
        if value is None:
            return None
        return decrypt(value)
