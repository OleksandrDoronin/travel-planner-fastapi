from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from repositories.user import UserRepository
from schemas.user import UserCreate, ShowUser
from security import get_password_hash
import logging

logger = logging.getLogger(__name__)


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
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if a user with the specified user email already exists.
        existing_user_by_email = await self.user_repository.get_user_by_email(
            email=user_data.email
        )
        if existing_user_by_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create a new User object with the provided data
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(password=user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
        )

        try:
            # Add the new user to the database
            saved_user = await self.user_repository.add_user_to_db(user=new_user)
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")  # Log the error
            raise HTTPException(
                status_code=400, detail=f"Database error: {err}"
            )  # Inform the client

        return ShowUser(
            user_id=saved_user.id,
            email=saved_user.email,
            username=saved_user.username,
            first_name=saved_user.first_name,
            last_name=saved_user.last_name,
            phone_number=saved_user.phone_number,
            is_active=saved_user.is_active,
        )
