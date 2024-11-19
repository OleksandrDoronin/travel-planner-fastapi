from unittest.mock import patch

import pytest
from httpx import AsyncClient
from settings import get_settings
from starlette import status

from tests.utils import extract_session_state


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


@pytest.mark.asyncio
@patch('src.auth.services.google_oauth.GoogleOAuthRepository.fetch_token')
@patch('src.auth.services.google_oauth.GoogleOAuthRepository.fetch_user_info')
async def test_google_callback_success(
    mock_fetch_user_info, mock_fetch_token, async_client: AsyncClient
):
    """
    Test successful Google OAuth callback handling using GoogleOAuthRepository.
    """
    # Mock responses
    mock_fetch_token.return_value = {
        'access_token': 'valid_access_token',
        'refresh_token': 'valid_refresh_token',
    }
    mock_fetch_user_info.return_value = {
        'id': '1234567890',
        'email': 'test_vasya@mail.com',
        'name': 'Vasya Lupin',
        'picture': 'https://example.com/avatar.png',
    }

    # Input parameters
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    test_code = 'mock_test_code'
    login_url = 'api/v1/auth/google/login/'
    callback_url = 'api/v1/auth/google/callback/'

    # Simulate a GET request to the login endpoint to retrieve session cookie
    login_response = await async_client.get(
        login_url, params={'redirect_uri': redirect_uri}
    )
    assert login_response.status_code == status.HTTP_200_OK

    # Extract session state from the cookie
    session_cookie = login_response.cookies.get('session')
    session_state = extract_session_state(session_cookie)

    # Simulate a GET request to the callback endpoint with the session state
    response = await async_client.get(
        callback_url,
        params={'code': test_code, 'state': session_state},
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    # Validate user information
    expected_user = {
        'email': 'test_vasya@mail.com',
        'full_name': 'Vasya Lupin',
        'profile_picture': 'https://example.com/avatar.png',
    }
    assert response_data['user'] == expected_user

    # Validate token information
    assert response_data['access_token'] == 'valid_access_token'
    assert response_data['refresh_token'] == 'valid_refresh_token'

