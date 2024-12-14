from cryptography.fernet import Fernet
from httpx import AsyncClient

from src.settings import settings


cypher = Fernet(settings.encryption_key.encode())


async def get_async_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client
