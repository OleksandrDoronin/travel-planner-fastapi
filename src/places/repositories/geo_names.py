import logging

import httpx

from src.places.constants import OPEN_CAGE_API_URL
from src.places.exceptions import GeoServiceError
from src.settings import settings


logger = logging.getLogger(__name__)


class GeoRepository:
    @staticmethod
    async def get_location_data(city: str, country: str) -> dict:
        """
        Checks whether the location specified by the city and country exists
        using OpenCage API.
        """
        params = {'q': f'{city}, {country}', 'key': settings.geo_name_data}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPEN_CAGE_API_URL, params=params)
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
