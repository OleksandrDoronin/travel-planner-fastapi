import logging
from datetime import date
from typing import Annotated, Optional

from database import get_db
from fastapi import Depends
from models import Place
from places.schemas.places import PlaceCreate, PlaceGet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger('travel_planner_app')


class PlaceRepository:
    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db_session = db_session

    async def create_place(self, user_id, place: PlaceCreate) -> PlaceGet:
        place = Place(**place.model_dump())
        place.user_id = user_id
        self.db_session.add(place)
        await self.db_session.commit()
        await self.db_session.refresh(place)
        return PlaceGet.model_validate(place)

    async def get_place_by_details(
        self,
        user_id: int,
        place_name: str,
        city: str,
        place_type: str,
        visit_date: Optional[date],
    ) -> Optional[PlaceGet]:
        stmt = select(Place).where(
            Place.user_id == user_id,
            Place.place_name == place_name,
            Place.city == city,
            Place.place_type == place_type,
            Place.visit_date == visit_date,
        )
        result = await self.db_session.execute(stmt)
        place = result.scalars().first()

        if place:
            return PlaceGet.model_validate(place)
        return None

    async def get_places_by_user(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> list[PlaceGet]:
        stmt = select(Place).where(Place.user_id == user_id).offset(offset).limit(limit)
        result = await self.db_session.execute(stmt)
        places = result.scalars().all()

        return [PlaceGet.model_validate(place) for place in places]

    async def get_place_by_id(self, place_id: int, user_id: int) -> Optional[PlaceGet]:
        stmt = select(Place).where(
            Place.id == place_id,
            Place.user_id == user_id,
        )
        result = await self.db_session.execute(stmt)
        place = result.scalars().first()

        if place:
            return PlaceGet.model_validate(place)
        return None
