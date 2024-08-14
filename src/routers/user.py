from fastapi import APIRouter, Depends
from starlette import status

from dependencies import get_user_service, get_auth_service
from schemas.user import ShowUser, UserCreate
from security import oauth2_scheme
from services.auth import AuthService
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


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ShowUser)
async def get_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    current_user = await auth_service.get_current_user_from_token(token=token)
    return await user_service.get_user_show(user_id=current_user.id)
