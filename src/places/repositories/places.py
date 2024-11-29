from typing import Annotated, Optional

from database import get_db
from fastapi import Depends
from models import Place
from places.schemas.places import PlaceCreate, PlaceGet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PlaceRepository:
    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db_session = db_session

    async def create_place(self, place: PlaceCreate) -> PlaceGet:
        place = Place(**place.model_dump())
        self.db_session.add(place)
        await self.db_session.commit()
        await self.db_session.refresh(place)
        return Place.model_validate(place)

    async def get_place(self, place_id: int, user_id: int) -> Optional[PlaceGet]:
        stmt = select(Place).where(Place.id == place_id, Place.user_id == user_id)
        result = await self.db_session.execute(stmt)
        place = result.scalar_one_or_none()

        if place:
            return Place.model_validate(place)
        return None

    async def get_places_by_user(self, user_id: int) -> list[PlaceGet]:
        stmt = select(Place).where(Place.user_id == user_id)
        result = await self.db_session.execute(stmt)
        places = result.scalars().all()

        return [Place.model_validate(place) for place in places]
