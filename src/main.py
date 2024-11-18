import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from auth.routers import google_auth, user
from database import get_db
from fastapi import FastAPI
from logging_config import setup_logging
from middleware import setup_middleware
from tasks.token_cleanup import remove_expired_tokens


setup_logging()
scheduler = AsyncIOScheduler()

logger = logging.getLogger('travel_planner_app')


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa F841
    """Controls the application lifecycle."""

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

app.include_router(google_auth.router, prefix='/api/v1')
app.include_router(user.router, prefix='/api/v1')
