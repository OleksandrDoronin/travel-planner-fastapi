import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums.places import PlaceRating, PlaceType, PlannedPlaceStatus
from src.repositories.postgres_base import Base


if TYPE_CHECKING:
    from src.models import User


class Place(Base):
    __tablename__ = 'places'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    place_name: Mapped[str]
    city: Mapped[str | None]
    country: Mapped[str | None]
    description: Mapped[str | None]
    photo_url: Mapped[str | None]
    rating: Mapped[PlaceRating | None] = mapped_column(Enum(PlaceRating))
    days_spent: Mapped[int | None]
    visit_date: Mapped[datetime.date | None]
    place_type: Mapped[PlaceType] = mapped_column(Enum(PlaceType))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship('User', back_populates='places')

    @property
    def is_favorite(self):
        return self.place_type == PlaceType.FAVORITE

    @property
    def is_visited(self):
        return self.place_type == PlaceType.VISITED


class PlannedPlace(Base):
    __tablename__ = 'planned_places'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    place_name: Mapped[str]
    city: Mapped[str | None]
    country: Mapped[str | None]
    description: Mapped[str | None]
    photo_url: Mapped[str | None]
    planned_visit_date: Mapped[datetime.date | None]
    planned_days_spent: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    planned_status: Mapped[PlannedPlaceStatus] = mapped_column(
        Enum(PlannedPlaceStatus), default=PlannedPlaceStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship('User', back_populates='planned_places')

    @property
    def is_planned(self):
        return True
