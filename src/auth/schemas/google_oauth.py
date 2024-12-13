from pydantic import BaseModel, EmailStr


class GoogleTokenResponse(BaseModel):
    """
    Response model for the Google OAuth token.
    """

    access_token: str
    expires_in: int
    refresh_token: str | None = None
    scope: str
    token_type: str
    id_token: str | None = None


class GoogleUserInfoResponse(BaseModel):
    """
    Response model for the Google user information.
    """

    id: str
    email: EmailStr
    verified_email: bool
    name: str
    given_name: str
    picture: str
