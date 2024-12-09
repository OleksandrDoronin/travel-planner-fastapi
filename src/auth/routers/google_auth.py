import logging
from typing import Annotated

from auth.schemas.auth_schemas import (
    GoogleCallBackResponse,
    GoogleLoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from auth.current_user import get_current_user
from auth.services.google_oauth import (
    GoogleAuthService,
    GoogleOAuthUrlGenerator,
)
from auth.services.token import TokenService
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from httpx import HTTPStatusError, RequestError
from jose import JWTError
from pydantic import HttpUrl
from settings import get_settings
from starlette import status


router = APIRouter(tags=['auth'], prefix='/auth')
logger = logging.getLogger('travel_planner_app')
settings = get_settings()


@router.get(
    '/google/login/',
    response_model=GoogleLoginResponse,
    summary='Generate Google OAuth Login URL',
)
async def google_login(
    request: Request,
    google_oauth_url_generator: Annotated[
        GoogleOAuthUrlGenerator, Depends(GoogleOAuthUrlGenerator)
    ],
    redirect_uri: HttpUrl = Query(..., alias='redirect_uri'),
) -> GoogleLoginResponse:
    """Generate Google OAuth URL and return it along with state."""

    try:
        google_auth_response, state = google_oauth_url_generator.generate_auth_url(
            redirect_uri=redirect_uri
        )
        request.session['state'] = state
        return google_auth_response

    except ValueError as e:
        logger.error(f'Error generating Google OAuth URL: {repr(e)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    '/google/callback/',
    response_model=GoogleCallBackResponse,
    status_code=status.HTTP_200_OK,
)
async def google_callback(
    request: Request,
    google_auth_service: Annotated[GoogleAuthService, Depends(GoogleAuthService)],
    redirect_uri: str = Query(settings.GOOGLE_REDIRECT_URI, description='Redirect uri'),
    code: str = Query(
        default=None, description='Authorization code provided by Google'
    ),
    state: str = Query(None, description='State parameter for CSRF protection'),
) -> GoogleCallBackResponse:
    """Handle the callback from Google OAuth after authorization."""

    # Retrieve session state for CSRF protection
    session_state = request.session.get('state')

    try:
        # Pass the received parameters to the service for processing
        callback_response = await google_auth_service.handle_google_callback(
            code=code,
            redirect_uri=redirect_uri,
            state=state,
            session_state=session_state,
        )
        return callback_response

    except ValueError as e:
        logger.error(f'Error in Google OAuth callback: {str(e)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPStatusError as e:
        logger.error(f'HTTP error when processing Google OAuth callback: {repr(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to fetch data from Google: {repr(e)}',
        )

    except RequestError as e:
        logger.error(f'Network error when processing Google OAuth callback: {repr(e)}')
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Network error occurred while fetching data from Google',
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
        token_service.validate_refresh_token(
            refresh_token=token_refresh_request.refresh_token
        )
        await token_service.blacklist_token(token=token_refresh_request.refresh_token)
        return {'detail': 'Successfully logged out.'}

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


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

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
