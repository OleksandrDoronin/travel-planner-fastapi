import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from src.auth.routers import google_auth, user
from src.config.database import get_db
from src.config.logging_config import setup_logging
from src.middleware import setup_middleware
from src.places.routers import places
from src.services.cache import CacheService
from src.tasks.token_cleanup import remove_expired_tokens


setup_logging()
scheduler = AsyncIOScheduler()

logger = logging.getLogger('travel_planner_app')


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa F841
    """Controls the application lifecycle."""

    # Checking the connection to Redis when the application starts
    redis_connected = await CacheService.check_connection()
    if not redis_connected:
        logger.warning(
            """Redis is not available.
            Some caching functionality may be unavailable."""
        )

    async def cleanup_task():
        """
        Periodically removes expired tokens from the `token_blacklist` table.

        This background task checks for tokens with expired `expires_at` timestamps and
        removes them from the database. It runs every 24 hours.
        """
        async for session in get_db():
            await remove_expired_tokens(session)
            logger.info('Expired tokens removed.')

    scheduler.add_job(
        cleanup_task,
        IntervalTrigger(hours=24),
        id='token_cleanup',
        replace_existing=True,
    )
    scheduler.start()
    try:
        logger.info('Application startup: Scheduler started.')
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title='Travel planner API', lifespan=lifespan)
setup_middleware(app)

pre = '/api/v1'
app.include_router(google_auth.router, prefix=pre)
app.include_router(user.router, prefix=pre)
app.include_router(places.router, prefix=pre)
