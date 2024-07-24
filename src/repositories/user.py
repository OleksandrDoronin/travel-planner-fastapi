from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db_session = db

    async def add_user_to_db(self, user: User) -> User:
        """Adds a new user to the database."""
        self.db_session.add(user)
        await self.db_session.flush()  # Flush to make sure changes are persisted
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user from the database by their username.
        """
        query = select(User).where(User.username == username)  # Construct the query
        result = await self.db_session.execute(query)  # Execute the query
        user = result.scalars().first()  # Retrieve the first user from the result
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user from the database by their ID.
        """
        query = select(User).where(User.user_id == user_id)  # Construct the query
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
