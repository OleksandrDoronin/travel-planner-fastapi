import logging

from auth.dependencies import get_current_user
from auth.schemas.user import ShowUser, UserCreate
from auth.services.user import UserService
from fastapi import APIRouter, Depends, HTTPException
from models.users import User
from sqlalchemy.exc import IntegrityError
from starlette import status


logger = logging.getLogger(__name__)


router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def create_user(user_data: UserCreate, user_service: UserService = Depends(UserService)) -> ShowUser:
    """
    Create a new user.

    This endpoint registers a new user in the database.
    """
    try:
        return await user_service.create_new_user(user_data=user_data)

    except IntegrityError as err:
        logger.error(f'Integrity error: {err}')
        raise HTTPException(status_code=400, detail=f'Database error: {err}')


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
) -> None:
    """
    Delete the currently authenticated user.

    This endpoint deletes the user who is currently authenticated.
    The user is identified by the token provided in the Authorization header
    """

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    await user_service.delete_user(user_id=current_user.id)


@router.get('/', status_code=status.HTTP_200_OK, response_model=ShowUser)
async def get_user(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
) -> ShowUser:
    """
    Retrieve the details of the current user.

    This endpoint returns the details of the currently authenticated user.
    The user is identified by the token provided in the Authorization header.
    """
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    user = await user_service.get_user_show(user_id=current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user
