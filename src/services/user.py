from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from db.models import User
from repositories.user import UserRepository
from schemas.user import UserCreate, ShowUser
from security import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db_session = db
        self.user_repository = UserRepository(db)

    async def create_new_user(self, user_data: UserCreate) -> ShowUser:
        """Creates a new user in the database.

        This function checks if a user with the specified email already exists."""

        # Check if a user with the specified username already exists.
        existing_user_by_username = await self.user_repository.get_user_by_username(
            username=user_data.username
        )
        if existing_user_by_username:
            raise ValueError("Username already registered")

        # Check if a user with the specified user email already exists.
        existing_user_by_email = await self.user_repository.get_user_by_email(
            email=user_data.email
        )
        if existing_user_by_email:
            raise ValueError("Email already registered")

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(password=user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
        )
        saved_user = await self.user_repository.add_user_to_db(user=new_user)
        return ShowUser(
            user_id=saved_user.id,
            email=saved_user.email,
            username=saved_user.username,
            first_name=saved_user.first_name,
            last_name=saved_user.last_name,
            phone_number=saved_user.phone_number,
            is_active=saved_user.is_active,
        )

    async def delete_user(self, user_id: UUID):
        return await self.user_repository.delete_user(user_id=user_id)

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        user = await self.user_repository.get_user_by_id(user_id=user_id)
        return user

    async def get_user_show(self, user_id: UUID) -> ShowUser:
        user = await self.get_user_by_id(user_id=user_id)
        return ShowUser(
            user_id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            is_active=user.is_active,
        )
