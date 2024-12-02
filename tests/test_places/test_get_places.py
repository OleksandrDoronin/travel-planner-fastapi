from httpx import AsyncClient
from starlette import status

from tests.utils import create_test_token


async def test_get_all_places(async_client: AsyncClient, mock_user_with_social_account):
    mock_user, _ = mock_user_with_social_account
    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/'

    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_200_OK


async def test_get_all_places_unauthorized(async_client: AsyncClient):
    invalid_token = 'test_token'
    url = 'api/v1/places/'
    response = await async_client.get(
        url, headers={'Authorization': f'Bearer {invalid_token}'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_place_by_id(
    async_client: AsyncClient, mock_user_with_social_account, mock_place
):
    mock_user, _ = mock_user_with_social_account
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == mock_place.id
    assert data['place_name'] == mock_place.place_name


async def test_get_place_by_id_unauthorized(async_client: AsyncClient, mock_place):
    invalid_token = 'test_token'
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.get(
        url, headers={'Authorization': f'Bearer {invalid_token}'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_place_by_id_invalid(
    async_client: AsyncClient, mock_user_with_social_account, mock_place
):
    mock_user, _ = mock_user_with_social_account
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{11111111111}'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Place with ID 11111111111 not found.'}
