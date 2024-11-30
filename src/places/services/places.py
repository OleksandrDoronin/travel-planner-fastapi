import logging
from datetime import date
from typing import Annotated, Optional

from fastapi import Depends
from places.repositories.geo_names import GeoNamesRepository
from places.repositories.places import PlaceRepository
from places.schemas.places import PlaceCreate, PlaceGet


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
