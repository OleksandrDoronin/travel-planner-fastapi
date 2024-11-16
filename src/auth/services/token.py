import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from auth.mapper import map_refresh_token
from auth.repositories.token_blacklist import TokenBlacklistRepository
from fastapi import Depends
from jose import JWTError, jwt
from settings import Settings, get_settings


logger = logging.getLogger('travel_planner_app')


class TokenService:
    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        token_repository: Annotated[
            TokenBlacklistRepository, Depends(TokenBlacklistRepository)
        ],
    ):
        self.settings = settings
        self.token_repository = token_repository

    def create_access_token(
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

    def create_refresh_token(self, user_id: int) -> str:
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

    def get_user_id_from_refresh_token(self, refresh_token: str) -> int:
        """Extracts user_id from the refresh token if valid."""
        payload = self.validate_refresh_token(refresh_token=refresh_token)
        user_id = payload['sub']
        return int(user_id)

    def validate_refresh_token(self, refresh_token: str) -> dict:
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

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Retrieves the expiration time from a token (exp)."""

        payload = self.validate_refresh_token(token)
        expires_at_timestamp = payload.get('exp')

        if expires_at_timestamp:
            return datetime.fromtimestamp(expires_at_timestamp, tz=timezone.utc)
        return None

    async def blacklist_token(self, token: str) -> None:
        """Adds a token to the blacklist."""

        expiration = self.get_token_expiration(token=token)

        if expiration:
            blacklist_entry = map_refresh_token(token=token, expires_at=expiration)
            await self.token_repository.add_token_to_blacklist(
                blacklist_entry=blacklist_entry
            )
        else:
            raise ValueError('Invalid token: Could not extract expiration')

    async def is_token_blacklisted(self, token: str) -> bool:
        """Checks if the token is on the blacklist."""
        return await self.token_repository.is_token_blacklisted(token=token)
