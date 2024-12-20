import logging
from datetime import date
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.models import Place
from src.places.exceptions import PlaceError
from src.places.schemas.filters import PlaceFilter
from src.places.schemas.places import PlaceCreationRequest, PlaceUpdateRequest


logger = logging.getLogger(__name__)


class PlaceRepository:
    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db_session = db_session

    async def create_place(self, user_id: int, place: PlaceCreationRequest) -> Place:
        """
        Creates a new place for the user.
        """
        try:
            place = Place(**place.model_dump())
            place.user_id = user_id

            self.db_session.add(place)
            await self.db_session.commit()
            await self.db_session.refresh(place)

            return place

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to create place for user {user_id}: {str(e)}')
            raise PlaceError()

    async def get_place_by_details(
        self,
        user_id: int,
        place_name: str,
        city: str,
        place_type: str,
        visit_date: date | None,
    ) -> Place | None:
        """
        Retrieves a place by its details.
        """
        try:
            stmt = select(Place).where(
                Place.user_id == user_id,
                Place.place_name == place_name,
                Place.city == city,
                Place.place_type == place_type,
                Place.visit_date == visit_date,
            )

            result = await self.db_session.execute(stmt)

            return result.scalars().first()

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to get place for user {user_id}: {str(e)}')
            raise PlaceError()

    async def get_places_by_user(
        self, filters: PlaceFilter, user_id: int, limit: int = 10, offset: int = 0
    ) -> list[Place]:
        """
        Retrieves places for a user with filters applied.
        """
        try:
            stmt = select(Place).where(Place.user_id == user_id).offset(offset).limit(limit)
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)

            result = await self.db_session.execute(stmt)
            places = [row for row in result.scalars()]

            return places

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to get places for user {user_id}: {str(e)}')
            raise PlaceError()

    async def get_place_by_id(self, place_id: int, user_id: int) -> Place | None:
        """
        Retrieves a place by ID and user ID.
        """
        try:
            stmt = select(Place).where(
                Place.id == place_id,
                Place.user_id == user_id,
            )
            result = await self.db_session.execute(stmt)

            return result.scalars().first()

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to get place by ID {place_id} for user {user_id}: {str(e)}')
            raise PlaceError()

    async def update_place(
        self, place_id: int, user_id: int, place_data: PlaceUpdateRequest
    ) -> Place | None:
        """
        Updates a place by ID and user ID.
        """
        try:
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

            return await self.db_session.get(Place, place_id)

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to update place by ID {place_id} for user {user_id}: {str(e)}')
            raise PlaceError()

    async def delete_place(self, place_id: int, user_id: int) -> bool:
        """
        Deletes a place by ID and user ID.
        """
        try:
            stmt = delete(Place).where(Place.id == place_id, Place.user_id == user_id)
            result = await self.db_session.execute(stmt)

            if result.rowcount == 0:
                return False

            await self.db_session.commit()

            return True

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to delete place by ID {place_id} for user {user_id}: {str(e)}')
            raise PlaceError()
