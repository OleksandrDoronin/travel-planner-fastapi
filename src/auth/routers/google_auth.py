import logging
from typing import Annotated

from auth.schemas.auth_schemas import GoogleCallBackResponse, GoogleLoginResponse
from auth.services.google_oauth import GoogleAuthService
from auth.services.google_oauth_url_generator import (
    GoogleOAuthUrlGenerator,
)
from auth.utils import generate_random_state
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import HttpUrl
from settings import get_settings
from starlette import status


router = APIRouter(tags=['auth'], prefix='/auth')
logger = logging.getLogger(__name__)
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
    try:
        state = generate_random_state()
        request.session['state'] = state
        google_auth_url = google_oauth_url_generator.get_google_auth_url(
            redirect_uri=redirect_uri, state=state
        )
        return google_auth_url

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.critical(f'Unexpected error: {repr(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error',
        )


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
    logger.info('Received Google callback with parameters: state=%s', session_state)

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error',
        )


@router.post('/logout')
async def logout():
    pass
