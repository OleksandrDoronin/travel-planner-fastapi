import logging
from typing import Annotated
from urllib.parse import urlencode, urlunparse

from auth.schemas.auth_schemas import GoogleAuthRequestSchema, GoogleLoginResponse
from fastapi import Depends
from settings import Settings, get_settings


logger = logging.getLogger('travel_planner_app')


class GoogleOAuthUrlGenerator:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    def get_google_auth_url(self, redirect_uri: str, state: str) -> GoogleLoginResponse:
        """Generates the Google OAuth URL."""
        try:
            google_auth_request = GoogleAuthRequestSchema(
                redirect_uri=redirect_uri, state=state
            )
            query_params = self._generate_query_params(
                google_auth_request=google_auth_request
            )
            google_auth_url = urlunparse(
                (
                    'https',
                    'accounts.google.com',
                    '/o/oauth2/v2/auth',
                    '',
                    urlencode(query_params),
                    '',
                )
            )
            return GoogleLoginResponse(url=google_auth_url)

        except Exception as e:
            logger.error(f'Failed to generate Google OAuth URL: {repr(e)}')
            raise ValueError('Failed to generate Google OAuth URL')

    def _generate_query_params(
        self, google_auth_request: GoogleAuthRequestSchema
    ) -> dict[str, str]:
        """Helper function to generate the OAuth query parameters."""
        return {
            'response_type': 'code',
            'client_id': self.settings.GOOGLE_OAUTH_KEY,
            'redirect_uri': google_auth_request.redirect_uri,
            'state': google_auth_request.state,
            'scope': 'email openid profile',
            'access_type': 'offline',
            'prompt': 'consent',
        }
