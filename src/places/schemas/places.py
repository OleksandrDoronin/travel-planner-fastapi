from datetime import date, datetime
from typing import Optional

from enums.places import PlaceRating, PlaceType
from places.utils import check_future_date
from pydantic import BaseModel, ConfigDict, conint, constr, field_validator


class PlaceCreate(BaseModel):
    """Schema for creating a place with field restrictions."""

    place_name: constr(min_length=3, max_length=100)
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[constr(min_length=0, max_length=500)] = None
    photo_url: Optional[str] = None
    rating: Optional[PlaceRating] = None
    days_spent: Optional[conint(ge=0, le=365)] = None
    visit_date: Optional[date] = None
    place_type: PlaceType

    model_config = ConfigDict(use_enum_values=True)

    @field_validator('visit_date')
    def check_visit_date(cls, visit_data):  # noqa
        return check_future_date(visit_date=visit_data)


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


class PlaceUpdate(BaseModel):
    """Schema for updating a place with optional fields."""

    place_name: Optional[constr(min_length=3, max_length=100)] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[constr(min_length=0, max_length=500)] = None
    photo_url: Optional[str] = None
    rating: Optional[PlaceRating] = None
    days_spent: Optional[conint(ge=0, le=365)] = None
    visit_date: Optional[date] = None
    place_type: Optional[PlaceType] = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    @field_validator('visit_date')
    def check_visit_date(cls, visit_data):  # noqa
        return check_future_date(visit_date=visit_data)
