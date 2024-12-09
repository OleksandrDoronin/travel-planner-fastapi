import logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from settings import get_settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware


settings = get_settings()
logger = logging.getLogger('travel_planner_app')


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            return JSONResponse(
                status_code=500, content={'detail': 'Internal server error'}
            )


def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(ErrorHandlingMiddleware)
