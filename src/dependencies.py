from typing import AsyncGenerator

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.pagination import PaginationParams
from src.repositories.postgres_base import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    async with async_session() as session:
        yield session


def get_pagination_params(
    offset: int = Query(
        0, ge=0, description='Offset for pagination (start from this index)'
    ),
    limit: int = Query(
        10, ge=1, le=100, description='Maximum number of entries per page (1 to 100)'
    ),
) -> PaginationParams:
    return PaginationParams(offset=offset, limit=limit)
