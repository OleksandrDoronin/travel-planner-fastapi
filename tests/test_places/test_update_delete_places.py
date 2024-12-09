import pytest
from httpx import AsyncClient
from starlette import status

from tests.utils import create_test_token


@pytest.mark.asyncio
async def test_update_place_by_id(async_client: AsyncClient, mock_user, mock_place):
    token = create_test_token(user_id=mock_user.id)

    url = f'api/v1/places/{mock_place.id}'

    # Get data before update
    response_before = await async_client.get(
        url, headers={'Authorization': f'Bearer {token}'}
    )

    assert response_before.status_code == status.HTTP_200_OK
    response_data_before = response_before.json()

    # Check that the data before updating matches the original
    assert response_data_before['place_name'] == mock_place.place_name
    assert response_data_before['city'] == mock_place.city
    assert response_data_before['country'] == mock_place.country
    assert response_data_before['rating'] == mock_place.rating

    # Updated data
    updated_place_data = {
        'place_name': 'My update place',
        'city': 'Paris',
        'country': 'France',
        'description': 'It is my dream',
        'photo_url': 'paris.ua',
        'rating': 4,
        'days_spent': 2,
        'visit_date': '2024-04-28',
        'place_type': 'visited',
    }

    # Send a request to update data
    response = await async_client.put(
        url,
        headers={'Authorization': f'Bearer {token}'},
        json=updated_place_data,
    )

    # Check that the data has been updated correctly
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['place_name'] == 'My update place'
    assert response_data['city'] == 'Paris'
    assert response_data['country'] == 'France'
    assert response_data['rating'] == 4


@pytest.mark.asyncio
async def test_update_place_by_id_invalid_city_and_country(
    async_client: AsyncClient, mock_user, mock_place
):
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{mock_place.id}'
    updated_place_data_invalid_city = {
        'place_name': 'My update place',
        'city': 'Par',
        'country': 'Fra',
        'description': 'It is my dream',
        'photo_url': 'paris.ua',
        'rating': 4,
        'days_spent': 2,
        'visit_date': '2024-04-28',
        'place_type': 'visited',
    }
    # Send a request to update data
    response = await async_client.put(
        url,
        headers={'Authorization': f'Bearer {token}'},
        json=updated_place_data_invalid_city,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_update_place_with_invalid_token(async_client: AsyncClient, mock_place):
    invalid_token = 'invalid.token.here'
    url = f'api/v1/places/{mock_place.id}'
    updated_place_data = {
        'place_name': 'Updated Place',
        'city': 'Paris',
        'country': 'France',
        'rating': 4,
    }
    response = await async_client.put(
        url,
        headers={'Authorization': f'Bearer {invalid_token}'},
        json=updated_place_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_place_by_id(async_client: AsyncClient, mock_user, mock_place):
    token = create_test_token(user_id=mock_user.id)
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.delete(
        url, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check place after deleting
    response_after_delete = await async_client.get(
        url, headers={'Authorization': f'Bearer {token}'}
    )
    assert response_after_delete.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_place_without_token(async_client: AsyncClient, mock_place):
    url = f'api/v1/places/{mock_place.id}'
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_place_other_user(
    async_client: AsyncClient, mock_place, another_user
):
    token = create_test_token(user_id=another_user.id)
    url = f'api/v1/places/{mock_place.id}'

    response = await async_client.delete(
        url, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
