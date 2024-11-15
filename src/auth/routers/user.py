from typing import Annotated

from auth.schemas.user_schemas import ShowUser
from auth.security import get_current_user
from fastapi import APIRouter, Depends
from starlette import status


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
