from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class SocialAccount(BaseModel):
    id: Optional[int] = None
    service: str
    social_account_id: str
    access_token: str
    refresh_token: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class SocialAccountResponse(BaseModel):
    service: str
    social_account_id: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: Optional[int] = None
    full_name: str
    username: Optional[str] = None
    email: EmailStr
    avatar: Optional[str]
    is_staff: bool = False
    is_active: bool = True
    is_pass_tutorial: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserResponse(User):
    social_accounts: list[SocialAccountResponse] = []

    model_config = ConfigDict(from_attributes=True)
