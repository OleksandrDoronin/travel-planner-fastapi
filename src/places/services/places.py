import logging
from typing import Annotated

from fastapi import Depends
from places.repositories.geo_names import GeoNamesRepository
from places.repositories.places import PlaceRepository
from places.schemas.places import PlaceCreate, PlaceGet
from places.utils import format_title_case

logger = logging.getLogger('travel_planner_app')

class PlaceService:
    def __init__(
        self,
        place_repository: Annotated[PlaceRepository, Depends(PlaceRepository)],
        geo_repository: Annotated[GeoNamesRepository, Depends(GeoNamesRepository)],
    ):
        self.place_repository = place_repository
        self.geo_repository = geo_repository

    async def create_place(self, user_id: int, place_data: PlaceCreate) -> PlaceGet:
        """
        Creates a new location after validating and formatting the data.
        """
        formatted_city, formatted_country = await self._format_location(
            place_data.city, place_data.country
        )
        await self._validate_location(formatted_city, formatted_country)
        await self._check_existing_place(user_id=user_id, place_id=place_data.id)

        place_data.city = formatted_city
        place_data.country = formatted_country

        try:
            return await self.place_repository.create_place(place=place_data)
        except Exception:
            raise

    @staticmethod
    async def _format_location(city: str, country: str) -> tuple[str, str]:
        return format_title_case(value=city), format_title_case(value=country)

    async def _validate_location(self, city: str, country: str) -> None:
        is_valid_location = await self.geo_repository.validate_location(
            city=city, country=country
        )
        if not is_valid_location:
            raise ValueError(f'City "{city}" in country "{country}" does not exist.')

    async def _check_existing_place(self, user_id: int, place_id: int) -> None:
        existing_place = await self.place_repository.get_place(
            place_id=place_id, user_id=user_id
        )
        if existing_place:
            raise ValueError('A place with this ID already exists for the user.')
