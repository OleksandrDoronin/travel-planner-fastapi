from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    ENCRYPTION_KEY: str

    # Google OAuth settings
    GOOGLE_OAUTH_KEY: str
    GOOGLE_OAUTH_SECRET: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_USERINFO_URL: str
    GOOGLE_REDIRECT_URI: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings():
    return Settings()
