import logging
from urllib.parse import urlencode, urlunparse

from src.auth.schemas.auth import GoogleAuthRequestSchema, GoogleLoginResponse
from src.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class GoogleOAuthUrlGenerator:
    @staticmethod
    def get_google_auth_url(
        redirect_uri: str, state: str
    ) -> GoogleLoginResponse:
        """Generates the Google OAuth URL."""

        google_auth_request = GoogleAuthRequestSchema(
            redirect_uri=redirect_uri, state=state
        )
        try:
            query_params = {
                'response_type': 'code',
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'redirect_uri': google_auth_request.redirect_uri,
                'state': google_auth_request.state,
                'scope': 'email openid profile',
                'access_type': 'offline',
                'prompt': 'consent',
            }
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
