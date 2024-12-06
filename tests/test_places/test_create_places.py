import pytest
from httpx import AsyncClient
from starlette import status

from tests.utils import create_test_token


@pytest.mark.asyncio
async def test_successful_create_place(async_client: AsyncClient, mock_user):
    """Test successful create place"""

    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/'
    place_data = {
        'place_name': 'Test place',
        'city': 'Kyiv',
        'country': 'Ukraine',
        'description': 'my favorite place',
        'photo_url': 'kyiv.ua',
        'rating': 5,
        'days_spent': 5,
        'visit_date': '2024-01-28',
        'place_type': 'visited',
    }
    response = await async_client.post(
        url,
        headers={'Authorization': f'Bearer {token}'},
        json=place_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['place_name'] == 'Test place'
    assert response_data['city'] == 'Kyiv'
    assert response_data['country'] == 'Ukraine'
    assert response_data['rating'] == 5


@pytest.mark.asyncio
async def test_create_place_with_invalid_city_and_country(
    async_client: AsyncClient, mock_user
):
    token = create_test_token(user_id=mock_user.id)

    url = 'api/v1/places/'
    place_data = {
        'place_name': 'Test place',
        'city': 'Greder',
        'country': 'Faler',
        'place_type': 'visited',
    }
    response = await async_client.post(
        url,
        headers={'Authorization': f'Bearer {token}'},
        json=place_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
