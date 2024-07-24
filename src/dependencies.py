from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from services.user import UserService


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Dependency function to get an instance of UserService
    """
    return UserService(db)
