import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


PHONE_NUMBER_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')
LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')


class TunedModel(BaseModel):
    """Base model with ORM compatibility."""

    class Config:
        """Tells pydantic to convert even non-dict obj to json"""

        from_attributes = True


class ShowUser(TunedModel):
    """Schema for representing a user in responses."""

    user_id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    phone_number: str


class UserCreate(BaseModel):
    """Schema for creating new users."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8, max_length=25)
    phone_number: str = Field(..., pattern=PHONE_NUMBER_PATTERN)

    @field_validator('first_name', 'last_name')
    def validate_first_name(cls, value: str) -> str:
        """Validate that first and last names contain only letters and hyphens."""
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError(
                'First name or last name should contain only letters and hyphens'
            )
        return value

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
