from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY: str
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings():
    return Settings()
