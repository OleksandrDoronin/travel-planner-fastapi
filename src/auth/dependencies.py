from functools import lru_cache

from cryptography.fernet import Fernet
from settings import get_settings


settings = get_settings()


@lru_cache
def get_cypher():
    return Fernet(settings.ENCRYPTION_KEY.encode())
