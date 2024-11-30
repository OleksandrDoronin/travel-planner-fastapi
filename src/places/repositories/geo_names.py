import httpx
from settings import get_settings


settings = get_settings()


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

        except httpx.HTTPStatusError:
            raise RuntimeError('HTTP error with OpenCage API')

        except httpx.RequestError:
            raise RuntimeError('Request error occurred')

        except Exception:
            raise
