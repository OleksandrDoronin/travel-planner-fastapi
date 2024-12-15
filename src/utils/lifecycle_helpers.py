import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.auth.repositories.token_blacklist import TokenBlacklistRepository
from src.dependencies import get_db
from src.services.cache import CacheService


logger = logging.getLogger(__name__)


def setup_scheduler():
    """Setting up the task scheduler."""
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # Add a token cleanup task
    add_token_cleanup_task(scheduler)

    return scheduler


def add_token_cleanup_task(scheduler):
    """Add the token cleanup task to the scheduler."""

    scheduler.add_job(
        cleanup_task,
        IntervalTrigger(hours=24),
        id='token_cleanup',
        replace_existing=True,
    )


async def cleanup_task():
    """Cleaning up obsolete tokens."""
    async for session in get_db():
        repository = TokenBlacklistRepository(db_session=session)

        removed_count = await repository.remove_expired_tokens()
        logger.info(f'Removed {removed_count} expired tokens.')


async def check_redis_connection():
    """Checking connection to Redis when starting the application."""

    await CacheService.check_connection()
