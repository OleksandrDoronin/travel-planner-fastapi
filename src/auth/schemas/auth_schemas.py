from datetime import datetime

from auth.schemas.user_schemas import UserResponse
from pydantic import BaseModel, ConfigDict, HttpUrl


class GoogleAuthRequestSchema(BaseModel):
    redirect_uri: HttpUrl
    state: str


class GoogleLoginResponse(BaseModel):
    url: HttpUrl


class GoogleCallBackResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str


class TokenBlacklistSchema(BaseModel):
    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
