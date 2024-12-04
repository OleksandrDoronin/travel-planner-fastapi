from datetime import datetime
from typing import TYPE_CHECKING, Optional

from config.database import Base
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from src.models.places import Place, PlannedPlace


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
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


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service: Mapped[str] = mapped_column(nullable=False)
    social_account_id: Mapped[str] = mapped_column(unique=True)
    access_token: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship('User', back_populates='social_accounts')
