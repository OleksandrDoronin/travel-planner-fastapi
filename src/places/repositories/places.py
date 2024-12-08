import logging
from datetime import date
from typing import Annotated, Optional

from config.database import get_db
from fastapi import Depends
from models import Place
from places.schemas.filters import PlaceFilter
from places.schemas.places import PlaceCreate, PlaceUpdate
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger('travel_planner_app')


class PlaceRepository:
    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db_session = db_session

    async def create_place(self, user_id, place: PlaceCreate) -> Place:
        place = Place(**place.model_dump())
        place.user_id = user_id
        self.db_session.add(place)
        await self.db_session.commit()
        await self.db_session.refresh(place)
        return place

    async def get_place_by_details(
        self,
        user_id: int,
        place_name: str,
        city: str,
        place_type: str,
        visit_date: Optional[date],
    ) -> Optional[Place]:
        stmt = select(Place).where(
            Place.user_id == user_id,
            Place.place_name == place_name,
            Place.city == city,
            Place.place_type == place_type,
            Place.visit_date == visit_date,
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_places_by_user(
        self, filters: PlaceFilter, user_id: int, limit: int = 10, offset: int = 0
    ):
        stmt = select(Place).where(Place.user_id == user_id).offset(offset).limit(limit)
        stmt = filters.filter(stmt)
        stmt = filters.sort(stmt)
        result = await self.db_session.execute(stmt)
        places = result.scalars().all()
        return places

    async def get_place_by_id(self, place_id: int, user_id: int) -> Optional[Place]:
        stmt = select(Place).where(
            Place.id == place_id,
            Place.user_id == user_id,
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def update_place(
        self, place_id: int, user_id: int, place_data: PlaceUpdate
    ) -> Optional[Place]:
        stmt = (
            update(Place)
            .where(Place.id == place_id, Place.user_id == user_id)
            .values(**place_data.model_dump())
            .execution_options(synchronize_session='fetch')
        )
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()

        if result.rowcount == 0:
            return None
        return await self.get_place_by_id(place_id=place_id, user_id=user_id)

    async def delete(self, place_id: int, user_id: int) -> bool:
        stmt = delete(Place).where((Place.id == place_id) & (Place.user_id == user_id))
        result = await self.db_session.execute(stmt)
        if result.rowcount == 0:
            return False
        await self.db_session.commit()
        return True
