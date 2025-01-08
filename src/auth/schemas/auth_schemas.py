from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.auth.schemas.user_schemas import UserWithSocialAccountsResponse


class GoogleAuthRequest(BaseModel):
    """Schema for Google authentication request parameters."""

    redirect_uri: HttpUrl
    state: str


class GoogleLoginResponse(BaseModel):
    """Response schema for initiating Google login."""

    url: str


class GoogleCallBackResponse(BaseModel):
    """Schema for the response after Google callback with user and token data."""

    user: UserWithSocialAccountsResponse
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request containing the refresh token."""

    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Schema for the response after refreshing tokens."""

    access_token: str
    refresh_token: str


class TokenBlacklistRequest(BaseModel):
    """Schema for adding tokens to the blacklist with expiration details."""

    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
