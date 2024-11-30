import logging

import httpx
from settings import get_settings


settings = get_settings()
logger = logging.getLogger('travel_planner_app')


class GeoRepository:
    @staticmethod
    async def validate_location(city: str, country: str) -> dict:
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
            logger.error(f'HTTP error with OpenCage API: {str(e)}')
            raise RuntimeError('Service error. Please try again later.')

        except httpx.RequestError as e:
            logger.error(f'Request error: {str(e)}')
            raise RuntimeError('Service unavailable. Please try again later.')

        except Exception as e:
            logger.critical(
                f'Unexpected error in GeoRepository: {str(e)}', exc_info=True
            )
            raise RuntimeError('An unexpected error occurred. Please contact support.')
