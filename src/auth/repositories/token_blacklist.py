from typing import Annotated, Optional

from auth.schemas.auth_schemas import TokenBlacklistSchema
from config.database import get_db
from fastapi import Depends
from models import TokenBlacklist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TokenBlacklistRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def add_token_to_blacklist(
        self, blacklist_entry: TokenBlacklistSchema
    ) -> None:
        """Adds a token to the blacklist."""

        blacklist_entry = TokenBlacklist(**blacklist_entry.model_dump())
        self.db_session.add(blacklist_entry)
        await self.db_session.commit()

    async def is_token_blacklisted(self, token: str) -> Optional[bool]:
        """Checks if the given token is blacklisted."""

        result = await self.db_session.execute(
            select(TokenBlacklist).where(TokenBlacklist.token == token)
        )
        return result.scalars().first() is not None
