from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.users import User


class UserRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db_session = db

    async def add_user_to_db(self, user: User) -> User:
        """Adds a new user to the database."""
        self.db_session.add(user)
        await self.db_session.flush()
        return user

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user from db"""
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalars().first()

        if user is None:
            raise NoResultFound(f'User with ID {user_id} not found')

        await self.db_session.delete(user)
        await self.db_session.commit()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user from the database by their username.
        """
        query = select(User).where(User.username == username)  # Construct the query
        result = await self.db_session.execute(query)  # Execute the query
        user = result.scalars().first()  # Retrieve the first user from the result
        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user from the database by their ID.
        """
        query = select(User).where(User.id == user_id)  # Construct the query
        result = await self.db_session.execute(query)  # Execute the query
        user = result.scalars().first()  # Retrieve the first user from the result
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user the database by their email
        """
        query = select(User).where(User.email == email)  # Construct the query
        result = await self.db_session.execute(query)  # Execute the query
        user = result.scalars().first()  # Retrieve the first user from the result
        return user
