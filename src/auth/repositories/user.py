from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.schemas.user_schemas import UserBase
from src.config.database import get_db
from src.models import User


class UserRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def get_user(self, **filters) -> Optional[UserBase]:
        """Get a user by given filters (e.g., email or id)."""
        stmt = (
            select(User).options(joinedload(User.social_accounts)).filter_by(**filters)
        )
        result = await self.db_session.execute(stmt)
        user = result.scalars().first()
        return UserBase.model_validate(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[UserBase]:
        """Get a user by email, using indexed field."""
        return await self.get_user(email=email)

    async def get_user_by_id(self, user_id: int) -> Optional[UserBase]:
        """Get a user by ID, using indexed field."""
        return await self.get_user(id=user_id)

    async def create_user(self, user: UserBase) -> UserBase:
        """Create a new user."""
        user_data = User(**user.model_dump())
        self.db_session.add(user_data)
        await self.db_session.commit()
        await self.db_session.refresh(user_data)
        return UserBase.model_validate(user_data)
