from datetime import datetime

from src.auth.schemas.auth_schemas import TokenBlacklistRequest


def map_refresh_token(token: str, expires_at: datetime) -> TokenBlacklistRequest:
    return TokenBlacklistRequest(token=token, expires_at=expires_at)
