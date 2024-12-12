from functools import lru_cache

from cryptography.fernet import Fernet
from httpx import AsyncClient

from src.settings import settings


@lru_cache
def get_cypher():
    return Fernet(settings.encryption_key.encode())


async def get_async_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client
