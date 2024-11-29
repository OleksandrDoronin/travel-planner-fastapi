import httpx
from settings import get_settings


settings = get_settings()


class GeoNamesRepository:
    @staticmethod
    async def validate_location(city: str, country: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'http://api.geonames.org/search',
                params={
                    'q': f'{city}, {country}',
                    'maxRows': 1,
                    'username': settings.GEONAMES_USERNAME,
                },
            )
            data = response.json()
            return len(data.get('geonames', [])) > 0
