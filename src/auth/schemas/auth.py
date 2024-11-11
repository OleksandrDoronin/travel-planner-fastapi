from pydantic import BaseModel, HttpUrl


class GoogleAuthRequestSchema(BaseModel):
    redirect_uri: HttpUrl
    state: str


class GoogleLoginResponse(BaseModel):
    url: HttpUrl
