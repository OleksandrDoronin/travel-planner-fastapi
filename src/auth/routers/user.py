from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.auth.current_user import get_current_user
from src.auth.schemas.user_schemas import ShowUser


router = APIRouter(tags=['user'], prefix='/user')


@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=ShowUser,
    summary='Get current user information',
)
async def get_user(
    current_user: Annotated[ShowUser, Depends(get_current_user)],
) -> ShowUser:
    return current_user
