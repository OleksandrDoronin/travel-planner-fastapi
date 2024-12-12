import logging
from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from src.auth.dependencies import get_async_client
from src.settings import settings


logger = logging.getLogger(__name__)


class GoogleOAuthRepository:
    def __init__(
        self,
        client: Annotated[AsyncClient, Depends(get_async_client)],
    ):
        self.client = client

    async def fetch_token(self, code: str, redirect_uri: str) -> dict:
        payload = {
            'code': code,
            'client_id': settings.google_oauth_key,
            'client_secret': settings.google_oauth_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        return await self._post(url=settings.google_token_url, data=payload)

    async def fetch_user_info(self, access_token: str) -> dict:
        params = {'access_token': access_token}
        return await self._get(url=settings.google_userinfo_url, params=params)

    async def _post(self, url: str, data: dict) -> dict:
        response = await self.client.post(url, data=data)
        response.raise_for_status()
        return response.json()

    async def _get(self, url: str, params: dict) -> dict:
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
