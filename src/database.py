from typing import AsyncGenerator

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=True,
)

async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    async with async_session() as session:
        yield session
