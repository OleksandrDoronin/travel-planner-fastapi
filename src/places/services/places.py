import logging
from typing import Annotated

from fastapi import Depends

from src.places.exceptions import (
    LocationValidationError,
    OpenAIError,
    PlaceAlreadyExistsError,
    PlaceNotFoundError,
)
from src.places.repositories.geo_names import GeoRepository
from src.places.repositories.openai import DescriptionOpenAIRepository
from src.places.repositories.places import PlaceRepository
from src.places.schemas.filters import PlaceFilter
from src.places.schemas.openai import PlaceDetailResponse
from src.places.schemas.places import PlaceCreationRequest, PlaceResponse, PlaceUpdateRequest
from src.places.utils.location_utils import format_location, generate_cache_key, is_location_valid
from src.places.utils.prompts import generate_description_prompt
from src.services.cache import CacheService


logger = logging.getLogger(__name__)


class PlaceService:
    def __init__(
        self,
        place_repository: Annotated[PlaceRepository, Depends(PlaceRepository)],
        geo_repository: Annotated[GeoRepository, Depends(GeoRepository)],
        cache_service: Annotated[CacheService, Depends(CacheService)],
        openai_repository: Annotated[
            DescriptionOpenAIRepository, Depends(DescriptionOpenAIRepository)
        ],
    ):
        self.place_repository = place_repository
        self.geo_repository = geo_repository
        self.cache_service = cache_service
        self.openai_repository = openai_repository

    async def create_place(self, user_id: int, place_data: PlaceCreationRequest) -> PlaceResponse:
        """
        Creates a new place after validating and formatting the data.

        Validates the location (city and country), checks for uniqueness,
        and then creates a new place entry.
        """

        # Format the city and country before validation
        formatted_city, formatted_country = format_location(
            city=place_data.city, country=place_data.country
        )

        # Validate the city and country
        await self._validate_location(city=formatted_city, country=formatted_country)

        # Ensure that the place is unique for the user
        await self._ensure_place_is_unique(
            user_id=user_id, place_data=place_data, formatted_city=formatted_city
        )

        # Generate description for the place
        place_detail = await self._generate_place_detail(
            place_data=place_data, city=formatted_city, country=formatted_country
        )

        place = await self.place_repository.create_place(
            place=place_data,
            user_id=user_id,
            place_detail=place_detail,
        )

        return PlaceResponse.model_validate(place)

    async def _generate_place_detail(
        self, place_data: PlaceCreationRequest, city: str, country: str
    ) -> PlaceDetailResponse:
        """
        Generates a description for a place using OpenAI.
        """
        description_prompt = generate_description_prompt(
            place_name=place_data.place_name,
            city=city,
            country=country,
        )

        try:
            description_response = await self.openai_repository.get_place_detail(
                prompt=description_prompt
            )
            return PlaceDetailResponse(
                description=description_response.description,
                photo_url=description_response.photo_url,
            )

        except Exception as e:
            logger.error(f'Error generating description: {e}')
            raise OpenAIError()

    async def _ensure_place_is_unique(
        self, user_id: int, place_data: PlaceCreationRequest, formatted_city: str
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
        Validates the city and country using the geo repository or cache.
        """
        location_data = await self._get_location_data(city=city, country=country)
        components = location_data.get('components', {})

        if not is_location_valid(components=components, city=city, country=country):
            raise LocationValidationError(city=city, country=country)

    async def _get_location_data(self, city: str, country: str) -> dict[str, str]:
        """
        Retrieves location data from cache or geo repository.

        If the data is not in the cache, fetches it from the geo repository and
        stores it in the cache.
        """
        cached_data = await self._get_cache_data(city=city, country=country)
        if cached_data:
            return cached_data

        location_data = await self.geo_repository.get_location_data(city=city, country=country)
        if not location_data:
            raise LocationValidationError(city=city, country=country)

        # Store the data in the cache
        cache_key = generate_cache_key(city=city, country=country)
        await self.cache_service.set_cache(key=cache_key, value=location_data)

        return location_data

    async def _get_cache_data(self, city: str, country: str) -> dict[str, str] | None:
        """
        Retrieves the location data from the cache using the generated key.
        """
        cache_key = generate_cache_key(city=city, country=country)

        return await self.cache_service.get_cache(key=cache_key)

    async def get_places(
        self, user_id: int, filters: PlaceFilter, offset: int, limit: int
    ) -> list[PlaceResponse]:
        """
        Retrieves a list of places for a given user with the provided filters,
        offset, and limit for pagination.
        """
        places = await self.place_repository.get_places_by_user(
            user_id=user_id, filters=filters, offset=offset, limit=limit
        )

        return [PlaceResponse.model_validate(place) for place in places]

    async def get_place_by_id(self, place_id: int, user_id: int) -> PlaceResponse:
        """
        Retrieves a place by its ID and user ID.
        """
        place = await self.place_repository.get_place_by_id(place_id=place_id, user_id=user_id)
        if not place:
            raise PlaceNotFoundError(place_id=place_id)

        return PlaceResponse.model_validate(place)

    async def update_place_by_id(self, place_id: int, user_id: int, place_data: PlaceUpdateRequest):
        """
        Updates an existing place by its ID, ensuring that the city and country
        are properly formatted and validated before saving the changes.
        """
        # Format the city and country before validation
        formatted_city, formatted_country = format_location(
            city=place_data.city, country=place_data.country
        )
        # Validate the city and country
        await self._validate_location(city=formatted_city, country=formatted_country)

        # Perform the update in the repository.
        place = await self.place_repository.update_place(
            place_id=place_id, user_id=user_id, place_data=place_data
        )
        if not place:
            raise PlaceNotFoundError(place_id=place_id)

        return PlaceResponse.model_validate(place)

    async def delete_place_by_id(self, place_id: int, user_id: int) -> None:
        """
        Deletes a place by its ID, ensuring that the place exists and is owned by the user.
        """
        deleted = await self.place_repository.delete_place(place_id=place_id, user_id=user_id)
        if not deleted:
            raise PlaceNotFoundError(place_id=place_id)
