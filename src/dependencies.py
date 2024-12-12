from fastapi import Query

from src.pagination import PaginationParams


def get_pagination_params(
    offset: int = Query(
        0, ge=0, description='Offset for pagination (start from this index)'
    ),
    limit: int = Query(
        10, ge=1, le=100, description='Maximum number of entries per page (1 to 100)'
    ),
) -> PaginationParams:
    return PaginationParams(offset=offset, limit=limit)
