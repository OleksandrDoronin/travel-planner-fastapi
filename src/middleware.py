from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.config import get_settings


settings = get_settings()


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
