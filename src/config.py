from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / 'test.db'


class Settings(BaseSettings):
    DATABASE_URL: str = f'sqlite+aiosqlite:///{DB_PATH}'
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
