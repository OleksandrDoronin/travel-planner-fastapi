import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
from starlette import status

from src.auth.schemas.user_schemas import UserBase
from src.auth.security import custom_bearer_scheme
from src.auth.services.token import TokenService
from src.auth.services.user import UserService


logger = logging.getLogger(__name__)


async def get_current_user(
    token_service: Annotated[TokenService, Depends(TokenService)],
    user_service: Annotated[UserService, Depends(UserService)],
    credentials: HTTPAuthorizationCredentials = Security(custom_bearer_scheme),
) -> UserBase:
    """
    Gets the current user based on the authorization token.

    Checks if the token is on a blacklist, extracts the user ID from the token
    and returns information about the user.
    """

    token = credentials.credentials

    # Check token blacklist
    await check_token_validity(token=token, token_service=token_service)

    try:
        # Extract the user ID from the token using the TokenService
        user_id = token_service.get_user_id_from_refresh_token(refresh_token=token)

        # Extract the user ID from the token using the TokenService
        user = await user_service.get_user_by_id(user_id=user_id)
        return user

    except JWTError as e:
        logger.error(f'JWT error: {str(e)}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    except ValueError as e:
        logger.error(f'Error in UserService: {str(e)}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


async def check_token_validity(token: str, token_service: TokenService) -> None:
    """
    Checks if the token is valid:
    - The token is not on the blacklist.
    - The token is in the correct format and has not expired.

    """
    if await token_service.is_token_blacklisted(token=token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
