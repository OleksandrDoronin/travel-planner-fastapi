from functools import lru_cache

from config import get_settings
from cryptography.fernet import Fernet


settings = get_settings()


@lru_cache
def get_cypher():
    return Fernet(settings.ENCRYPTION_KEY.encode())
