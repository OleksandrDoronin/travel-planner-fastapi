import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str


class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    JWT_SECRET_KEY: str
    ENCRYPTION_KEY: str


class OAuthSettings(BaseSettings):
    GOOGLE_OAUTH_KEY: str
    GOOGLE_OAUTH_SECRET: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_USERINFO_URL: str
    GOOGLE_REDIRECT_URI: str


class GeonamesSettings(BaseSettings):
    OPEN_CAGE_DATA: str
    OPEN_CAGE_URL: str


class RedisSettings(BaseSettings):
    REDIS_URL: str


class Settings(
    DatabaseSettings,
    SecuritySettings,
    OAuthSettings,
    GeonamesSettings,
    RedisSettings,
):
    pass


@lru_cache
def get_settings() -> Settings:
    """Getting settings based on the current environment."""

    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # noqa
    dotenv_file = os.path.join(os.path.dirname(__file__), f'../.env.{ENVIRONMENT}')
    if not load_dotenv(dotenv_file):
        raise FileNotFoundError(f'Environment file {dotenv_file} not found.')

    return Settings()
