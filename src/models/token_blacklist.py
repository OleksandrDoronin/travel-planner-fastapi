from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.postgres_base import Base


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    token: Mapped[str] = mapped_column(index=True)
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime]
