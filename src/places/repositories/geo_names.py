import logging

import httpx

from src.places.exceptions import GeoServiceError
from src.settings import get_settings


settings = get_settings()
logger = logging.getLogger('travel_planner_app')


class GeoRepository:
    @staticmethod
    async def get_location_data(city: str, country: str) -> dict:
        """
        Checks whether the location specified by the city and country exists
        using OpenCage API.
        """
        params = {'q': f'{city}, {country}', 'key': settings.OPEN_CAGE_DATA}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.OPEN_CAGE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if 'results' not in data or len(data['results']) == 0:
                return {}

            return data['results'][0]

        except httpx.HTTPStatusError as e:
            logger.error(f'HTTP error for {city}, {country}: {e}')
            raise GeoServiceError()

        except httpx.RequestError as e:
            logger.error(f'Request error for {city}, {country}: {e}')
            raise GeoServiceError()

        except Exception as e:
            logger.error(f'Unexpected error for {city}, {country}: {e}', exc_info=True)
            raise GeoServiceError()
