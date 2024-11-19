import pytest
from httpx import AsyncClient
from settings import get_settings
from starlette import status


settings = get_settings()


@pytest.mark.asyncio
async def test_google_login(async_client: AsyncClient):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    login_endpoint = 'api/v1/auth/google/login/'
    google_oauth_base_url = 'https://accounts.google.com/o/oauth2/'

    response = await async_client.get(
        login_endpoint, params={'redirect_uri': redirect_uri}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'url' in response.json()
    assert response.json()['url'].startswith(google_oauth_base_url)
