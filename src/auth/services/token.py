import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends
from jose import JWTError, jwt
from settings import Settings, get_settings


logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    async def create_access_token(
        self, user_id: int, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Creates a new access token."""
        to_encode = {'sub': str(user_id)}
        expire = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta
            else timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE)
        )
        to_encode.update({'exp': expire})
        access_token = jwt.encode(
            to_encode, self.settings.JWT_SECRET_KEY, self.settings.ALGORITHM
        )
        return access_token

    async def create_refresh_token(self, user_id: int) -> str:
        """Creates a new refresh token."""
        to_encode = {'sub': str(user_id)}
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.settings.REFRESH_TOKEN_EXPIRE
        )
        to_encode.update({'exp': expire})
        refresh_token = jwt.encode(
            to_encode, self.settings.JWT_SECRET_KEY, self.settings.ALGORITHM
        )
        return refresh_token

    async def validate_refresh_token(self, refresh_token: str) -> dict:
        """Validates the refresh token and returns the payload if valid."""
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
            exp = payload.get('exp')

            if exp is None or datetime.now(timezone.utc) >= datetime.fromtimestamp(
                exp, tz=timezone.utc
            ):
                raise JWTError('Refresh token has expired.')

            user_id = payload.get('sub')
            if user_id is None:
                raise JWTError('Invalid refresh token: User ID not found in payload.')

            return payload

        except JWTError as e:
            logger.error(f'JWT error: {str(e)}')
            raise
