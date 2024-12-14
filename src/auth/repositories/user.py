import logging
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.exceptions import GoogleOAuthError
from src.auth.schemas.user_schemas import UserBase, UserFilter
from src.dependencies import get_db
from src.models import User


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def get_user(self, filters: UserFilter) -> Optional[UserBase]:
        """Get a user by given filters."""
        try:
            stmt = select(User).options(joinedload(User.social_accounts))

            if filters.email:
                stmt = stmt.filter(User.email == filters.email)

            if filters.user_id:
                stmt = stmt.filter(User.id == filters.user_id)

            result = await self.db_session.execute(stmt)
            user = result.scalars().first()

            return UserBase.model_validate(user) if user else None

        except SQLAlchemyError as e:
            logger.error(f'Failed to get user: {str(e)}')
            raise GoogleOAuthError()

    async def get_user_by_email(self, email: str) -> Optional[UserBase]:
        """Get a user by email."""
        filters = UserFilter(email=email)

        return await self.get_user(filters)

    async def get_user_by_id(self, user_id: int) -> Optional[UserBase]:
        """Get a user by ID."""
        filters = UserFilter(user_id=user_id)

        return await self.get_user(filters)

    async def create_user(self, user: UserBase) -> UserBase:
        """Create a new user."""
        try:
            user_data = User(**user.model_dump())
            self.db_session.add(user_data)
            await self.db_session.commit()
            await self.db_session.refresh(user_data)
            return UserBase.model_validate(user_data)

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to create user: {str(e)}')
            raise GoogleOAuthError()
