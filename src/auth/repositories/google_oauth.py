import logging
from typing import Annotated

from auth.dependencies import get_async_client
from fastapi import Depends
from httpx import AsyncClient, HTTPStatusError
from settings import Settings, get_settings


logger = logging.getLogger('travel_planner_app')


class GoogleOAuthRepository:
    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        client: Annotated[AsyncClient, Depends(get_async_client)],
    ):
        self.client = client
        self.settings = settings

    async def fetch_token(self, code: str, redirect_uri: str) -> dict:
        payload = {
            'code': code,
            'client_id': self.settings.GOOGLE_OAUTH_KEY,
            'client_secret': self.settings.GOOGLE_OAUTH_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        return await self._post(url=self.settings.GOOGLE_TOKEN_URL, data=payload)

    async def fetch_user_info(self, access_token: str) -> dict:
        params = {'access_token': access_token}
        return await self._get(url=self.settings.GOOGLE_USERINFO_URL, params=params)

    async def _post(self, url: str, data: dict) -> dict:
        try:
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            logger.error(
                f'HTTP error {e.response.status_code} when accessing {url}: {repr(e)}'
            )
            raise ValueError(f'Failed to fetch data from {url}')
        except Exception as e:
            logger.error(f'Unexpected error fetching data from {url}: {repr(e)}')
            raise ValueError('Unexpected error occurred')

    async def _get(self, url: str, params: dict) -> dict:
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            logger.error(
                f'HTTP error {e.response.status_code} when accessing {url}: {repr(e)}'
            )
            raise ValueError(f'Failed to fetch data from {url}')
        except Exception as e:
            logger.error(f'Unexpected error fetching data from {url}: {repr(e)}')
            raise ValueError('Unexpected error occurred')
