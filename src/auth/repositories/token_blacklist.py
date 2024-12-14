import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import GoogleOAuthError
from src.auth.schemas.auth_schemas import TokenBlacklistRequest
from src.dependencies import get_db
from src.models import TokenBlacklist


logger = logging.getLogger(__name__)


class TokenBlacklistRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def add_token_to_blacklist(self, blacklist_entry: TokenBlacklistRequest) -> None:
        """Adds a token to the blacklist."""
        try:
            blacklist_entry = TokenBlacklist(**blacklist_entry.model_dump())

            self.db_session.add(blacklist_entry)
            await self.db_session.commit()

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to add token to blacklist: {e}')
            raise GoogleOAuthError()

    async def is_token_blacklisted(self, token: str) -> bool:
        """Checks if the given token is blacklisted."""
        try:
            result = await self.db_session.execute(
                select(TokenBlacklist).where(TokenBlacklist.token == token)
            )

            return result.scalars().first() is not None

        except SQLAlchemyError as e:
            logger.error(f'Failed to check if token is blacklisted: {e}')
            raise GoogleOAuthError()
