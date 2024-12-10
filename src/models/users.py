from datetime import datetime
from typing import TYPE_CHECKING, Optional

from config.database import Base
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from src.models import Place, PlannedPlace, SocialAccount


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    profile_picture: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    gender: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    social_accounts: Mapped[list['SocialAccount']] = relationship(
        'SocialAccount', back_populates='user'
    )
    places: Mapped[list['Place']] = relationship('Place', back_populates='user')
    planned_places: Mapped[list['PlannedPlace']] = relationship(
        'PlannedPlace', back_populates='user'
    )
