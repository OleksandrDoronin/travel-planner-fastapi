from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class SocialAccountLink(BaseModel):
    """Model for a linked social account."""

    id: Optional[int] = None
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

    id: Optional[int] = None
    full_name: str
    email: EmailStr
    profile_picture: Optional[str]
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Response model for a user, including linked social accounts."""

    id: Optional[int] = None
    social_accounts: list[SocialAccountResponse] = []


class ShowUser(UserResponse):
    """Extended user response model that includes additional fields."""

    bio: Optional[str] = None
    gender: Optional[str] = None
