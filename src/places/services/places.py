import logging
from datetime import date
from typing import Annotated, Optional

from fastapi import Depends
from places.repositories.geo_names import GeoRepository
from places.repositories.places import PlaceRepository
from places.schemas.places import PlaceCreate, PlaceGet
from places.utils import format_title_case


logger = logging.getLogger('travel_planner_app')


class PlaceService:
    def __init__(
        self,
        place_repository: Annotated[PlaceRepository, Depends(PlaceRepository)],
        geo_repository: Annotated[GeoRepository, Depends(GeoRepository)],
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

        await self._check_existing_place(
            user_id=user_id,
            city=place_data.city,
            place_name=place_data.place_name,
            place_type=place_data.place_type,
            visit_date=place_data.visit_date,
        )

        try:
            return await self.place_repository.create_place(
                place=place_data, user_id=user_id
            )
        except Exception:
            raise

    async def _check_existing_place(
        self,
        user_id: int,
        place_name: str,
        city: str,
        place_type: str,
        visit_date: Optional[date],
    ) -> None:
        existing_place = await self.place_repository.get_place_by_details(
            user_id=user_id,
            place_name=place_name,
            city=city,
            place_type=place_type,
            visit_date=visit_date,
        )

        if existing_place:
            raise ValueError(
                f'The place "{place_name}" in city "{city}" with type "{place_type}"'
                f' and visit date "{visit_date}" already exists for this user.'
            )

    @staticmethod
    async def _format_location(city: str, country: str) -> tuple:
        return format_title_case(value=city), format_title_case(value=country)

    async def _validate_location(self, city: str, country: str) -> None | bool:
        formatted_city, formatted_country = await self._format_location(
            city=city, country=country
        )

        location_data = await self.geo_repository.validate_location(
            city=formatted_city, country=formatted_country
        )

        if not location_data:
            raise ValueError(
                f'City "{formatted_city}" or country "{formatted_country}" '
                f'does not exist.'
            )

        components = location_data.get('components', {})

        if 'city' not in components or 'country' not in components:
            raise ValueError(
                f'Invalid city or country in response for {formatted_city}, '
                f'{formatted_country}.'
            )

        city_matches = components['city'].lower() == formatted_city.lower()
        country_matches = components['country'].lower() == formatted_country.lower()

        if not city_matches or not country_matches:
            raise ValueError(
                f'City "{formatted_city}" or country "{formatted_country}" '
                f'does not match the API response.'
            )
        return True

    async def get_places(self, user_id: int) -> list[PlaceGet]:
        return await self.place_repository.get_places_by_user(user_id=user_id)

    async def get_place_by_id(self, place_id: int, user_id: int) -> PlaceGet:
        place = await self.place_repository.get_place_by_id(
            place_id=place_id, user_id=user_id
        )
        if not place:
            raise ValueError(f'Place with ID {place_id} not found.')
        return place
