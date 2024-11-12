from pydantic import BaseModel, HttpUrl


class GoogleAuthRequestSchema(BaseModel):
    redirect_uri: HttpUrl
    state: str


class GoogleLoginResponse(BaseModel):
    url: HttpUrl


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
