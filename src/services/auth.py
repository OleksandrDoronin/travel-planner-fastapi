from fastapi.params import Depends
from jose import jwt, JWTError
from fastapi import HTTPException
from starlette import status

from config import settings
from db.models import User
from repositories.user import UserRepository
from security import bcrypt_context


class AuthService:
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    async def authenticate_user(self, username: str, password: str) -> bool | User:
        user = await self.user_repository.get_user_by_username(username=username)
        if not user:
            return False
        if not bcrypt_context.verify(password, user.hashed_password):
            return False
        return user

    async def get_current_user_from_token(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = await self.user_repository.get_user_by_username(username=username)
        if user is None:
            raise credentials_exception
        return user
