from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.settings import settings


Base = declarative_base()

engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=True,
)

async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
