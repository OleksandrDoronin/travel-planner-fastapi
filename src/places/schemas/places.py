from datetime import date, datetime
from typing import Optional

from enums.places import PlaceRating, PlaceType
from pydantic import BaseModel, ConfigDict, conint, constr, field_validator


class PlaceCreate(BaseModel):
    """Schema for creating a place with field restrictions."""

    place_name: constr(min_length=3, max_length=100)
    city: str
    country: str
    description: Optional[constr(min_length=0, max_length=500)] = None
    photo_url: Optional[str] = None
    rating: Optional[PlaceRating] = None
    days_spent: Optional[conint(ge=0, le=365)] = None
    visit_date: Optional[date] = None
    place_type: PlaceType

    model_config = ConfigDict(use_enum_values=True)

    @field_validator('visit_date')
    def check_future_date(cls, v):  # noqa
        if v and v > date.today():
            raise ValueError('Date of visit cannot be in the future')
        return v


class PlaceGet(BaseModel):
    """Schema for retrieving a place with fields returned from the database."""

    id: int
    place_name: str
    city: str
    country: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    rating: Optional[PlaceRating] = None
    days_spent: Optional[int] = None
    visit_date: Optional[date] = None
    place_type: PlaceType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
