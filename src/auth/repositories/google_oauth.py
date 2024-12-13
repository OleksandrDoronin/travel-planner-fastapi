import logging
from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from src.auth.dependencies import get_async_client
from src.auth.exceptions import GoogleOAuthError
from src.auth.schemas.google_oauth import GoogleTokenResponse, GoogleUserInfoResponse
from src.settings import settings


logger = logging.getLogger(__name__)


class GoogleOAuthRepository:
    def __init__(
        self,
        client: Annotated[AsyncClient, Depends(get_async_client)],
    ):
        self.client = client

    async def fetch_token(self, code: str, redirect_uri: str) -> GoogleTokenResponse:
        payload = {
            'code': code,
            'client_id': settings.google_oauth_key,
            'client_secret': settings.google_oauth_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        try:
            response_data = await self._post(
                url=settings.google_token_url, data=payload
            )
            return GoogleTokenResponse(**response_data)
        except Exception:
            raise GoogleOAuthError()

    async def fetch_user_info(self, access_token: str) -> GoogleUserInfoResponse:
        params = {'access_token': access_token}
        try:
            response_data = await self._get(
                url=settings.google_userinfo_url, params=params
            )
            return GoogleUserInfoResponse(**response_data)
        except Exception:
            raise GoogleOAuthError()

    async def _post(self, url: str, data: dict) -> dict:
        response = await self.client.post(url, data=data)
        if response.status_code != 200:
            raise GoogleOAuthError()
        return response.json()

    async def _get(self, url: str, params: dict) -> dict:
        response = await self.client.get(url, params=params)
        if response.status_code != 200:
            raise GoogleOAuthError()
        return response.json()
