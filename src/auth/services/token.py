import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from jose import JWTError, jwt

from src.auth.exceptions import TokenError
from src.auth.mapper import map_refresh_token
from src.auth.repositories.token_blacklist import TokenBlacklistRepository
from src.auth.repositories.user import UserRepository
from src.auth.schemas.auth_schemas import TokenRefreshResponse
from src.settings import settings


logger = logging.getLogger(__name__)


class TokenService:
    def __init__(
        self,
        token_repository: Annotated[TokenBlacklistRepository, Depends(TokenBlacklistRepository)],
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
    ):
        self.token_repository = token_repository
        self.user_repository = user_repository

    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
        """Creates a new access token."""
        to_encode = {'sub': str(user_id)}
        expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire)
        )
        to_encode.update({'exp': expire})

        access_token = jwt.encode(to_encode, settings.jwt_secret_key, settings.algorithm)

        return access_token

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Creates a new refresh token."""
        to_encode = {'sub': str(user_id)}
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire)
        to_encode.update({'exp': expire})

        refresh_token = jwt.encode(to_encode, settings.jwt_secret_key, settings.algorithm)

        return refresh_token

    @staticmethod
    def validate_refresh_token(refresh_token: str) -> dict:
        """Validates the refresh token and returns the payload if valid."""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt_secret_key,
                algorithms=[settings.algorithm],
            )
            exp = payload.get('exp')

            if exp is None or datetime.now(timezone.utc) >= datetime.fromtimestamp(
                exp, tz=timezone.utc
            ):
                logger.warning('Refresh token expired or invalid expiration timestamp')
                raise TokenError()

            user_id = payload.get('sub')
            if user_id is None:
                logger.warning(f'User with ID {user_id} not found for token refresh.')
                raise TokenError()

            return payload
        except JWTError as e:
            logger.error(f'JWTError while validating refresh token: {str(e)}')
            raise TokenError()

    async def _get_user_by_id(self, user_id: int):
        """Checks if the refresh token is on a blacklist."""
        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if not user:
            logger.warning(f'User with ID {user_id} not found for token validation.')
            raise TokenError()

        return user

    def get_user_id_from_refresh_token(self, refresh_token: str) -> int:
        """Extracts user_id from the refresh token if valid."""
        try:
            payload = self.validate_refresh_token(refresh_token=refresh_token)
            user_id = payload['sub']

            return int(user_id)

        except JWTError as e:
            logger.error(f'JWTError while extracting user_id from refresh token: {str(e)}')
            raise TokenError()

    def get_token_expiration(self, token: str) -> datetime | None:
        """Retrieves the expiration time from a token (exp)."""
        try:
            payload = self.validate_refresh_token(refresh_token=token)
            expires_at_timestamp = payload.get('exp')

            if expires_at_timestamp:
                return datetime.fromtimestamp(expires_at_timestamp, tz=timezone.utc)

            return None

        except JWTError:
            logger.error('Error retrieving expiration time from token')
            raise TokenError()

    async def blacklist_token(self, token: str) -> None:
        """Adds a token to the blacklist."""
        try:
            expiration = self.get_token_expiration(token=token)

            if expiration:
                blacklist_entry = map_refresh_token(token=token, expires_at=expiration)
                await self.token_repository.add_token_to_blacklist(blacklist_entry=blacklist_entry)
            else:
                logger.warning('Failed to get expiration for token')
                raise TokenError()

        except JWTError as e:
            logger.error(f'JWTError while blacklisting token: {str(e)}')
            raise TokenError()

    async def is_token_blacklisted(self, token: str) -> bool:
        """Checks if the token is on the blacklist."""
        return await self.token_repository.is_token_blacklisted(token=token)

    async def refresh_token_and_blacklist(self, refresh_token: str) -> TokenRefreshResponse:
        """
        Refreshes the access token and adds the old refresh token to the blacklist.
        """
        try:
            await self._check_if_token_blacklisted(refresh_token)

            user_id = self.get_user_id_from_refresh_token(refresh_token)

            user = await self._get_user_by_id(user_id)

            new_access_token, new_refresh_token = self._generate_new_tokens(user)

            await self.blacklist_token(token=refresh_token)

            return TokenRefreshResponse(
                access_token=new_access_token, refresh_token=new_refresh_token
            )

        except JWTError as e:
            logger.error(f'JWTError while refreshing and blacklisting the token: {str(e)}')
            raise TokenError()

    async def _check_if_token_blacklisted(self, refresh_token: str) -> None:
        """Checks if the refresh token is on a blacklist."""
        if await self.token_repository.is_token_blacklisted(token=refresh_token):
            raise TokenError()

    def _generate_new_tokens(self, user) -> tuple[str, str]:
        """Generates new access and refresh tokens for the user."""
        new_access_token = self.create_access_token(user_id=user.id)
        new_refresh_token = self.create_refresh_token(user_id=user.id)

        return new_access_token, new_refresh_token
