import logging
from typing import Annotated

import httpx
from fastapi import Depends
from settings import Settings, get_settings


logger = logging.getLogger(__name__)


class GoogleOAuthClient:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    async def fetch_token(self, code: str, redirect_uri: str) -> dict:
        """Fetches Google OAuth token using an authorization code."""
        payload = {
            'code': code,
            'client_id': self.settings.GOOGLE_OAUTH_KEY,
            'client_secret': self.settings.GOOGLE_OAUTH_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        return await self._post_request(
            url=self.settings.GOOGLE_TOKEN_URL, data=payload
        )

    async def fetch_user_info(self, access_token: str) -> dict:
        """Fetches user info using the access token."""
        params = {'access_token': access_token}
        return await self._get_request(
            url=self.settings.GOOGLE_USERINFO_URL, params=params
        )

    @staticmethod
    async def _post_request(url: str, data: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f'HTTP error {e.response.status_code} when accessing {url}: {repr(e)}'
            )
            raise ValueError(f'Failed to fetch data from {url}')
        except Exception as e:
            logger.error(f'Unexpected error fetching data from {url}: {repr(e)}')
            raise ValueError('Unexpected error occurred')

    @staticmethod
    async def _get_request(url: str, params: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f'HTTP error {e.response.status_code} when accessing {url}: {repr(e)}'
            )
            raise ValueError(f'Failed to fetch data from {url}')
        except Exception as e:
            logger.error(f'Unexpected error fetching data from {url}: {repr(e)}')
            raise ValueError('Unexpected error occurred')
