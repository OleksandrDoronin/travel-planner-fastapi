import logging
from typing import Annotated
from urllib.parse import urlencode, urlunparse

from auth.schemas.auth_schemas import GoogleAuthRequestSchema, GoogleLoginResponse
from auth.utils import generate_random_state
from fastapi import Depends
from settings import Settings, get_settings


logger = logging.getLogger('travel_planner_app')


class GoogleOAuthUrlGenerator:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    def generate_auth_url(self, redirect_uri: str) -> tuple[GoogleLoginResponse, str]:
        """Generate the Google OAuth URL and manage the state."""
        try:
            state = self._generate_state()
            google_auth_url = self._get_google_auth_url(redirect_uri, state)
            return GoogleLoginResponse(url=google_auth_url), state
        except ValueError as e:
            logger.error(f'Error generating Google OAuth URL: {repr(e)}')
            raise ValueError('Failed to generate Google OAuth URL')

    @staticmethod
    def _generate_state() -> str:
        """Generate a random state string."""
        return generate_random_state()

    def _get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Helper to generate the Google OAuth URL."""
        google_auth_request = GoogleAuthRequestSchema(
            redirect_uri=redirect_uri, state=state
        )

        query_params = self._generate_query_params(google_auth_request)

        return urlunparse(
            (
                'https',
                'accounts.google.com',
                '/o/oauth2/v2/auth',
                '',
                urlencode(query_params),
                '',
            )
        )

    def _generate_query_params(
        self, google_auth_request: GoogleAuthRequestSchema
    ) -> dict:
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
