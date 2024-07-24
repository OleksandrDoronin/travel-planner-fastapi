from fastapi import APIRouter, Depends
from starlette import status

from dependencies import get_user_service
from schemas.user import ShowUser, UserCreate
from services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> ShowUser:
    """
    Create a new user.

    This endpoint registers a new user in the database.
    """
    return await user_service.create_new_user(user_data=user_data)
