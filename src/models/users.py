from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    profile_picture: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    gender: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    social_account = relationship('SocialAccount', back_populates='user', uselist=False)


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service: Mapped[str]
    social_account_id: Mapped[str] = mapped_column(unique=True)
    access_token: Mapped[Optional[str]] = mapped_column(unique=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='social_account')
