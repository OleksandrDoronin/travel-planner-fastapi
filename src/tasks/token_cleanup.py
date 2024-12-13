import logging
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.token_blacklist import TokenBlacklist


logger = logging.getLogger(__name__)


async def remove_expired_tokens(db_session: AsyncSession):
    """Deletes expired tokens."""
    query = delete(TokenBlacklist).where(TokenBlacklist.expires_at < datetime.now(timezone.utc))
    result = await db_session.execute(query)
    await db_session.commit()
    logger.info(f'Removed {result.rowcount} expired tokens.')
