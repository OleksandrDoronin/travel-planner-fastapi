import logging
from typing import Annotated

from fastapi import Depends

from src.places.exceptions import LocationValidationError, PlaceAlreadyExistsError
from src.places.repositories.geo_names import GeoRepository
from src.places.repositories.places import PlaceRepository
from src.places.schemas.filters import PlaceFilter
from src.places.schemas.places import PlaceCreate, PlaceGet, PlaceUpdate
from src.places.utils import format_title_case
from src.services.cache import CacheService


logger = logging.getLogger(__name__)


class PlaceService:
    def __init__(
        self,
        place_repository: Annotated[PlaceRepository, Depends(PlaceRepository)],
        geo_repository: Annotated[GeoRepository, Depends(GeoRepository)],
        cache_service: Annotated[CacheService, Depends(CacheService)],
    ):
        self.place_repository = place_repository
        self.geo_repository = geo_repository
        self.cache_service = cache_service

    async def create_place(self, user_id: int, place_data: PlaceCreate) -> PlaceGet:
        """
        Creates a new location after validating and formatting the data.

        This method validates the location data (city and country),
        ensures the place is unique for the user, and then creates a new place entry.
        """

        # Format the city and country before validation
        formatted_city, formatted_country = self._format_location(
            city=place_data.city, country=place_data.country
        )
        # Validate the city and country
        await self._validate_location(city=formatted_city, country=formatted_country)

        # Ensure that the place is unique for this user
        await self._ensure_place_is_unique(
            user_id=user_id, place_data=place_data, formatted_city=formatted_city
        )

        place = await self.place_repository.create_place(place=place_data, user_id=user_id)
        return PlaceGet.model_validate(place)

    async def _ensure_place_is_unique(
        self, user_id: int, place_data: PlaceCreate, formatted_city: str
    ) -> None:
        """
        Ensures that the place is unique for the user by checking if it already exists.
        """

        existing_place = await self.place_repository.get_place_by_details(
            user_id=user_id,
            place_name=place_data.place_name,
            city=formatted_city,
            place_type=place_data.place_type,
            visit_date=place_data.visit_date,
        )
        if existing_place:
            raise PlaceAlreadyExistsError(
                place_name=place_data.place_name,
                city=formatted_city,
                place_type=place_data.place_type,
            )

    async def _validate_location(self, city: str, country: str) -> None:
        """
        Validates city and country using the geo repository or cache.
        """

        location_data = await self._get_location_data_from_cache_or_api(city=city, country=country)
        components = location_data.get('components', {})
        if not self._is_location_valid(components, city, country):
            raise LocationValidationError(city=city, country=country)

    async def _get_location_data_from_cache_or_api(self, city: str, country: str):
        """
        Tries to get the location data from cache, if not available calls
        the geo repository.

        This method first checks the cache for location data. If it's not found,
        it queries the geo repository and stores the result in the cache.
        """
        # Generate a cache key
        cache_key = f'geo_{city}_{country}'

        # Attempt to get the data from the cache
        cached_data = await self.cache_service.get_cache(key=cache_key)
        if cached_data:
            return cached_data

        location_data = await self.geo_repository.get_location_data(city=city, country=country)
        if not location_data:
            raise LocationValidationError(city=city, country=country)

        # Store the data in the cache
        await self.cache_service.set_cache(key=cache_key, value=location_data)
        return location_data

    @staticmethod
    def _is_location_valid(components: dict, city: str, country: str) -> bool:
        """
        Checks if the API response matches the provided city and country.
        """

        return (
            components.get('city', '').lower() == city.lower()
            and components.get('country', '').lower() == country.lower()
        )

    @staticmethod
    def _format_location(city: str, country: str) -> tuple[str, str]:
        """
        Formats the city and country into title case.
        """
        return format_title_case(value=city), format_title_case(value=country)

    async def get_places(
        self, user_id: int, filters: PlaceFilter, offset: int, limit: int
    ) -> list[PlaceGet]:
        places = await self.place_repository.get_places_by_user(
            user_id=user_id, filters=filters, offset=offset, limit=limit
        )
        return [PlaceGet.model_validate(place) for place in places]

    async def get_place_by_id(self, place_id: int, user_id: int) -> PlaceGet:
        place = await self.place_repository.get_place_by_id(place_id=place_id, user_id=user_id)
        if not place:
            raise ValueError(f'Place with ID {place_id} not found.')
        return PlaceGet.model_validate(place)

    async def update_place_by_id(self, place_id: int, user_id: int, place_data: PlaceUpdate):
        """
        Updates the place by ID, ensuring that city and country
        are properly formatted and validated.
        """

        # Format the city and country before validation
        formatted_city, formatted_country = self._format_location(
            city=place_data.city, country=place_data.country
        )
        # Validate the city and country
        await self._validate_location(city=formatted_city, country=formatted_country)

        place = await self.place_repository.update_place(
            place_id=place_id, user_id=user_id, place_data=place_data
        )
        if not place:
            raise ValueError(f'Place with ID {place_id} not found or is not owned by user.')
        return PlaceGet.model_validate(place)

    async def delete_place_by_id(self, place_id: int, user_id: int) -> None:
        deleted = await self.place_repository.delete(place_id=place_id, user_id=user_id)
        if not deleted:
            raise ValueError(f'Place with ID {place_id} not found or is not owned by user.')
