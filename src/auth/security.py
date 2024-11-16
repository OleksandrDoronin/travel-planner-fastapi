import logging
from typing import Annotated

from auth.schemas.user_schemas import UserBase
from auth.services.token import TokenService
from auth.services.user import UserService
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from starlette import status


logger = logging.getLogger('travel_planner_app')

http_bearer = HTTPBearer()


async def get_current_user(
    token_service: Annotated[TokenService, Depends(TokenService)],
    user_service: Annotated[UserService, Depends(UserService)],
    credentials: HTTPAuthorizationCredentials = Security(http_bearer),
) -> UserBase:
    """
    Gets the current user based on the authorization token.

    Checks if the token is on a blacklist, extracts the user ID from the token
    and returns information about the user.
    """

    token = credentials.credentials

    if await token_service.is_token_blacklisted(token=token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
        )

    try:
        # Extract the user ID from the token using the TokenService
        user_id = token_service.get_user_id_from_refresh_token(refresh_token=token)

        # Extract the user ID from the token using the TokenService
        user = await user_service.get_user_by_id(user_id=user_id)
        return user

    except JWTError as e:
        logger.error(f'JWT error: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
        )

    except ValueError as e:
        logger.error(f'Error in UserService: {str(e)}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error',
        )
