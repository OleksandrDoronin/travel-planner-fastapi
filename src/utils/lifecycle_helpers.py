import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config.database import get_db
from src.services.cache import CacheService
from src.tasks.token_cleanup import remove_expired_tokens


logger = logging.getLogger('travel_planner_app')


def setup_scheduler():
    """Setting up the task scheduler."""
    scheduler = AsyncIOScheduler()
    scheduler.start()
    logger.info('Scheduler started.')

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
        await remove_expired_tokens(session)


async def check_redis_connection():
    """Checking connection to Redis when starting the application."""

    await CacheService.check_connection()
