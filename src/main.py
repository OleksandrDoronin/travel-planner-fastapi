from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routers import google_auth, user
from src.config.logging_config import setup_logging
from src.middleware import setup_middleware
from src.places.routers import places
from src.utils.lifecycle_helpers import (
    check_redis_connection,
    setup_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa F841
    """Controls the application lifecycle."""

    # Setting up the scheduler
    scheduler = setup_scheduler()

    # Checking connection to Redis
    await check_redis_connection()

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""

    setup_logging()
    travel_app = FastAPI(title='Travel planner API', lifespan=lifespan)

    # Setup middleware and routers
    setup_middleware(travel_app)
    pre = '/api/v1'
    travel_app.include_router(google_auth.router, prefix=pre)
    travel_app.include_router(user.router, prefix=pre)
    travel_app.include_router(places.router, prefix=pre)

    return travel_app


app = create_app()
