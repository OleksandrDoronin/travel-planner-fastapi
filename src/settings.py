import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


env_file = os.getenv('ENV_FILE', '.env')
load_dotenv(dotenv_path=env_file)


class DatabaseSettings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+asyncpg://'
            f'{self.postgres_user}:'
            f'{self.postgres_password}@'
            f'{self.postgres_host}:{self.postgres_port}/'
            f'{self.postgres_db}'
        )


class SecuritySettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire: int
    refresh_token_expire: int
    jwt_secret_key: str
    encryption_key: str


class OAuthSettings(BaseSettings):
    google_oauth_key: str
    google_oauth_secret: str
    google_redirect_uri: str


class GeonamesSettings(BaseSettings):
    geo_name_data: str


class RedisSettings(BaseSettings):
    redis_url: str


class OpenaiSettings(BaseSettings):
    openai_api_key: str
    pydantic_ai_model: str


class Settings(
    DatabaseSettings,
    SecuritySettings,
    OAuthSettings,
    GeonamesSettings,
    RedisSettings,
    OpenaiSettings,
):
    model_config = SettingsConfigDict(
        env_file=env_file,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # noqa


settings = get_settings()
