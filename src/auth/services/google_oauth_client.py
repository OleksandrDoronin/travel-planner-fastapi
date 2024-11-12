import logging

import httpx

from src.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class GoogleOAuthClient:
    @staticmethod
    async def fetch_token(code: str, redirect_uri: str) -> dict:
        """Fetches Google OAuth token using an authorization code."""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    'code': code,
                    'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                    'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code',
                }
                response = await client.post(
                    settings.GOOGLE_TOKEN_URL, data=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f'HTTP error occurred while fetching token: {repr(e)}'
            )
            raise ValueError('Failed to fetch token from Google')
        except Exception as e:
            logger.error(f'Failed to fetch token from Google: {repr(e)}')
            raise ValueError('Failed to fetch token from Google')

    @staticmethod
    async def fetch_user_info(access_token: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                params = {'access_token': access_token}
                response = await client.get(
                    settings.GOOGLE_USERINFO_URL, params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f'HTTP error occurred while fetching user info: {repr(e)}'
            )
            raise ValueError('Error fetching user info')
        except Exception as e:
            logger.error(f'Failed to fetch user info from Google: {repr(e)}')
            raise ValueError('Error fetching user info')
