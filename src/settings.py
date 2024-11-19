import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    ENVIRONMENT: str

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    ENCRYPTION_KEY: str
    JWT_SECRET_KEY: str

    # Google OAuth settings
    GOOGLE_OAUTH_KEY: str
    GOOGLE_OAUTH_SECRET: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_USERINFO_URL: str
    GOOGLE_REDIRECT_URI: str


@lru_cache
def get_settings() -> Settings:
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # noqa
    if ENVIRONMENT == 'development':
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.development'))
        return Settings()

    elif ENVIRONMENT == 'production':
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.production'))
        return Settings()

    elif ENVIRONMENT == 'test':
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))
        return Settings()

    else:
        raise ValueError(f'Unknown environment: {ENVIRONMENT}')
