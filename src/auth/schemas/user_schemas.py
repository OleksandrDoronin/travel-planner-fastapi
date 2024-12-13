from pydantic import BaseModel, ConfigDict, EmailStr


class SocialAccountLink(BaseModel):
    """Model for a linked social account."""

    id: int | None = None
    service: str
    social_account_id: str
    access_token: str
    refresh_token: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class SocialAccountResponse(BaseModel):
    """Response model for a linked social account."""

    service: str
    social_account_id: str
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base model for user data, to be used in various responses."""

    id: int | None = None
    full_name: str
    email: EmailStr
    profile_picture: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserWithSocialAccountsResponse(UserBase):
    """Response model for a user, including linked social accounts."""

    id: int | None = None
    social_accounts: list[SocialAccountResponse] = []


class ExtendedUserResponse(UserWithSocialAccountsResponse):
    """Extended user response model that includes additional fields."""

    bio: str | None = None
    gender: str | None = None
