from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_ALEMBIC: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()
