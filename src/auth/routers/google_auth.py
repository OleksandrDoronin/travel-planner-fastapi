import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import HttpUrl
from starlette import status

from src.auth.schemas.auth import GoogleLoginResponse
from src.auth.services.google_oauth_url_generator import (
    GoogleOAuthUrlGenerator,
)
from src.auth.utils import generate_random_state


router = APIRouter(tags=['auth'], prefix='/auth')
logger = logging.getLogger(__name__)


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


@router.get('/google/callback/', status_code=status.HTTP_200_OK)
async def google_callback():
    pass


@router.post('/logout')
async def logout():
    pass
