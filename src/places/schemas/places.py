from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, conint, constr, field_validator

from src.enums.places import PlaceRating, PlaceType
from src.places.utils.date_utils import check_future_date


class PlaceCreationRequest(BaseModel):
    """Schema for creating a place with field restrictions."""

    place_name: constr(min_length=3, max_length=100)
    city: str | None = None
    country: str | None = None
    description: constr(min_length=0, max_length=500) | None = None
    rating: PlaceRating | None = None
    days_spent: conint(ge=0, le=365) | None = None
    visit_date: date | None = None
    place_type: PlaceType

    model_config = ConfigDict(use_enum_values=True)

    @field_validator('visit_date')
    def check_visit_date(cls, visit_data):  # noqa
        return check_future_date(visit_date=visit_data)


class PlaceResponse(BaseModel):
    """Schema for retrieving a place with fields returned from the database."""

    id: int
    place_name: str
    city: str
    country: str
    description: str | None = None
    photo_url: str | None = None
    rating: PlaceRating | None = None
    days_spent: int | None = None
    visit_date: date | None = None
    place_type: PlaceType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class PlaceUpdateRequest(BaseModel):
    """Schema for updating a place with optional fields."""

    place_name: constr(min_length=3, max_length=100) | None = None
    city: str | None = None
    country: str | None = None
    description: constr(min_length=0, max_length=500) | None = None
    photo_url: str | None = None
    rating: PlaceRating | None = None
    days_spent: conint(ge=0, le=365) | None = None
    visit_date: date | None = None
    place_type: PlaceType | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    @field_validator('visit_date')
    def check_visit_date(cls, visit_data):  # noqa
        return check_future_date(visit_date=visit_data)
