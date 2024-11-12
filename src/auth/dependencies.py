from functools import lru_cache

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException

from src.auth.security import oauth2_scheme
from src.auth.services.auth import AuthService
from src.config import get_settings
from src.models.users import User


settings = get_settings()


async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends()
) -> User:
    user = await auth_service.get_current_user_from_token(token)
    if user is None:
        raise HTTPException(
            status_code=401, detail='Invalid authentication credentials'
        )
    return user


@lru_cache
def get_cypher():
    return Fernet(settings.ENCRYPTION_KEY.encode())
