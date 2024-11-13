from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class BaseModelWithConfig(BaseModel):
    """Base model class that includes common configuration for all models."""

    model_config = ConfigDict(from_attributes=True)


class SocialAccountLink(BaseModelWithConfig):
    """Model for a linked social account."""

    id: Optional[int] = None
    service: str
    social_account_id: str
    access_token: str
    refresh_token: str
    user_id: int


class SocialAccountResponse(BaseModelWithConfig):
    """Response model for a linked social account."""

    service: str
    social_account_id: str


class UserBase(BaseModelWithConfig):
    """Base model for user data, to be used in various responses."""

    full_name: str
    username: Optional[str] = None
    email: EmailStr
    avatar: Optional[str]
    is_staff: bool = False
    is_active: bool = True
    is_pass_tutorial: bool = False


class UserResponse(UserBase):
    """Response model for a user, including linked social accounts."""

    id: Optional[int] = None
    social_accounts: list[SocialAccountResponse] = []
