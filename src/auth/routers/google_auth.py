import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import HttpUrl
from starlette import status

from src.auth.current_user import get_current_user
from src.auth.exceptions import GoogleOAuthError, TokenError
from src.auth.schemas.auth_schemas import (
    GoogleCallBackResponse,
    GoogleLoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from src.auth.services.google_oauth import (
    GoogleAuthService,
    GoogleOAuthUrlGenerator,
)
from src.auth.services.token import TokenService
from src.auth.utils.cache_utils import generate_and_cache_state, verify_state
from src.services.cache import CacheService
from src.settings import settings


router = APIRouter(tags=['auth'], prefix='/auth')
logger = logging.getLogger(__name__)


@router.get(
    '/google/login/',
    response_model=GoogleLoginResponse,
    summary='Generate Google OAuth Login URL',
)
async def google_login(
    google_oauth_url_generator: Annotated[
        GoogleOAuthUrlGenerator, Depends(GoogleOAuthUrlGenerator)
    ],
    cache_service: Annotated[CacheService, Depends(CacheService)],
    redirect_uri: HttpUrl = Query(alias='redirect_uri'),
) -> GoogleLoginResponse:
    """Generate Google OAuth URL and return it along with state."""

    try:
        state = await generate_and_cache_state(cache_service=cache_service)

        google_auth_response = await google_oauth_url_generator.generate_auth_url(
            redirect_uri=redirect_uri, state=state
        )

        return google_auth_response

    except GoogleOAuthError as e:
        logger.exception('Error generating Google OAuth URL')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    '/google/callback/',
    response_model=GoogleCallBackResponse,
    status_code=status.HTTP_200_OK,
)
async def google_callback(
    google_auth_service: Annotated[GoogleAuthService, Depends(GoogleAuthService)],
    cache_service: Annotated[CacheService, Depends(CacheService)],
    token_service: Annotated[TokenService, Depends(TokenService)],
    redirect_uri: str = Query(settings.google_redirect_uri, description='Redirect uri'),
    code: str = Query(description='Authorization code provided by Google'),
    state: str = Query(description='State parameter for CSRF protection'),
) -> GoogleCallBackResponse:
    """Handle the callback from Google OAuth after authorization."""

    try:
        verified_state = await verify_state(cache_service=cache_service, state=state)

        # Pass the received parameters to the service for processing
        user_response = await google_auth_service.handle_google_callback(
            code=code,
            redirect_uri=redirect_uri,
            state=verified_state['state'],
        )

        new_access_token = token_service.create_access_token(user_id=user_response.id)
        new_refresh_token = token_service.create_refresh_token(user_id=user_response.id)

        return GoogleCallBackResponse(
            user=user_response,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    except GoogleOAuthError as e:
        logger.exception('Google OAuth error occurred.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )
    except TokenError as e:
        logger.exception('Error with token.')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    '/logout',
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    summary='Logout the user and blacklist the token',
)
async def logout(
    token_refresh_request: Annotated[TokenRefreshRequest, Body(...)],
    token_service: Annotated[TokenService, Depends(TokenService)],
) -> dict[str, str]:
    """Logs out the user by blacklisting the provided refresh token."""

    try:
        token_service.validate_refresh_token(refresh_token=token_refresh_request.refresh_token)
        await token_service.blacklist_token(token=token_refresh_request.refresh_token)
        return {'detail': 'Successfully logged out.'}

    except TokenError as e:
        logger.exception('Error with token.')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    except GoogleOAuthError as e:
        logger.exception('Google OAuth error occurred.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


@router.post(
    '/token/refresh',
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Refresh the access token',
)
async def refresh_token(
    token_refresh_request: Annotated[TokenRefreshRequest, Body(...)],
    token_service: Annotated[TokenService, Depends(TokenService)],
) -> TokenRefreshResponse:
    """Refreshes access and refresh tokens by invalidating the old refresh token."""

    try:
        tokens = await token_service.refresh_token_and_blacklist(
            refresh_token=token_refresh_request.refresh_token
        )
        return tokens

    except TokenError as e:
        logger.exception('Error with token.')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    except GoogleOAuthError as e:
        logger.exception('Google OAuth error occurred.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )
