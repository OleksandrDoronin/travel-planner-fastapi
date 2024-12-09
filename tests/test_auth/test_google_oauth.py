from unittest.mock import patch

import pytest
from httpx import AsyncClient
from settings import get_settings
from starlette import status

from tests.utils import create_test_token, extract_session_state


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

    assert 'user' in response_data
    assert response_data['user']['email'] == 'test_vasya@mail.com'
    assert response_data['user']['full_name'] == 'Vasya Lupin'
    assert response_data['user']['profile_picture'] == 'https://example.com/avatar.png'
    assert 'access_token' in response_data
    assert 'refresh_token' in response_data


@pytest.mark.asyncio
async def test_update_refresh_access_token_blacklist(
    async_client: AsyncClient, mock_user
):
    """
    Test that a refresh token can be used to generate new access and refresh tokens,
    and that the old refresh token is blacklisted after usage.
    """

    token = create_test_token(user_id=mock_user.id)
    endpoint = 'api/v1/auth/token/refresh'

    # First request to refresh the tokens should succeed
    response = await async_client.post(endpoint, json={'refresh_token': token})
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert 'access_token' in response_data
    assert 'refresh_token' in response_data

    # Second request with the same refresh token should fail with 401 Unauthorized
    response = await async_client.post(endpoint, json={'refresh_token': token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client: AsyncClient):
    endpoint = 'api/v1/auth/token/refresh'
    invalid_token = 'invalid_token'
    response = await async_client.post(endpoint, json={'refresh_token': invalid_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, mock_user):
    token = create_test_token(user_id=mock_user.id)
    token_request = token
    endpoint = 'api/v1/auth/logout'
    response = await async_client.post(
        endpoint,
        headers={'Authorization': f'Bearer {token}'},
        json={'refresh_token': token_request},
    )
    assert response.status_code == status.HTTP_200_OK
    # assert response.json() == {'detail': 'Successfully logged out.'}


@pytest.mark.asyncio
async def test_logout_user_not_found(async_client: AsyncClient):
    endpoint = 'api/v1/auth/logout'
    non_existent_user_token = create_test_token(user_id=99999)

    response = await async_client.post(
        endpoint,
        headers={'Authorization': f'Bearer {non_existent_user_token}'},
        json={'refresh_token': 'some_refresh_token'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_logout_unauthorized(async_client: AsyncClient):
    endpoint = 'api/v1/auth/logout'

    response = await async_client.post(
        endpoint, json={'refresh_token': 'some_refresh_token'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}

    invalid_token = 'invalid_token'
    response = await async_client.post(
        endpoint,
        headers={'Authorization': f'Bearer {invalid_token}'},
        json={'refresh_token': 'some_refresh_token'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid token'}
