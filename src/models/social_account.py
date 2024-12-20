from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repositories.postgres_base import Base


if TYPE_CHECKING:
    from src.models import User


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    service: Mapped[str]
    social_account_id: Mapped[str]
    access_token: Mapped[str | None] = mapped_column(unique=True)
    refresh_token: Mapped[str | None] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship('User', back_populates='social_accounts')
