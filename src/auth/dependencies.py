from functools import lru_cache

from cryptography.fernet import Fernet
from httpx import AsyncClient

from src.settings import get_settings


settings = get_settings()


@lru_cache
def get_cypher():
    return Fernet(settings.ENCRYPTION_KEY.encode())


async def get_async_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client
