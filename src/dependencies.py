from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.models import User
from security import oauth2_scheme
from services.auth import AuthService
from services.user import UserService


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Dependency function to get an instance of UserService
    """
    return UserService(db)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency function to get an instance of AuthService
    """
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.get_current_user_from_token(token)
