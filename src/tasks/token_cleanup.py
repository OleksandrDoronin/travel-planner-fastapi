import logging
from datetime import datetime, timezone

from models.token_blacklist import TokenBlacklist
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger('travel_planner_app')


async def remove_expired_tokens(db_session: AsyncSession):
    """Deletes expired tokens."""
    query = delete(TokenBlacklist).where(
        TokenBlacklist.expires_at < datetime.now(timezone.utc)
    )
    result = await db_session.execute(query)
    await db_session.commit()
    logger.info(f'Removed {result.rowcount} expired tokens.')
