import pytest
from httpx import AsyncClient
from starlette import status

from tests.utils import create_test_token


@pytest.mark.asyncio
async def test_get_all_places(async_client: AsyncClient, mock_user, mock_place):
    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/'

    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['place_name'] == mock_place.place_name


@pytest.mark.asyncio
async def test_get_all_places_unauthorized(async_client: AsyncClient):
    invalid_token = 'test_token'
    url = 'api/v1/places/'
    response = await async_client.get(
        url, headers={'Authorization': f'Bearer {invalid_token}'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_place_by_id(async_client: AsyncClient, mock_user, mock_place):
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == mock_place.id
    assert data['place_name'] == mock_place.place_name


@pytest.mark.asyncio
async def test_get_place_by_id_unauthorized(async_client: AsyncClient, mock_place):
    invalid_token = 'test_token'
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.get(
        url, headers={'Authorization': f'Bearer {invalid_token}'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_place_by_id_invalid(
    async_client: AsyncClient, mock_user, mock_place
):
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{11111111111}'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Place with ID 11111111111 not found.'}


@pytest.mark.asyncio
async def test_get_places_by_filter(async_client: AsyncClient, mock_user, mock_place):
    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/?cities=Kyiv&place_type=visited'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == mock_place.id
    assert data[0]['place_name'] == mock_place.place_name


@pytest.mark.asyncio
async def test_get_places_by_filter_non_existent(
    async_client: AsyncClient, mock_user, mock_place
):
    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/?cities=test&place_type=no'
    response = await async_client.get(url, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data == []
