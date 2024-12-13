from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import ConfigDict, Field, field_validator

from src.models import Place


class PlaceFilter(Filter):
    place_name__in: Optional[list[str]] = Field(default=None, alias='names')
    city__in: Optional[list[str]] = Field(default=None, alias='cities')
    country__in: Optional[list[str]] = Field(default=None, alias='countries')
    place_type__in: Optional[list[str]] = Field(default=None, alias='types')

    # Sorting parameters
    order_by: Optional[list[str]] = Field(default=None, alias='sortByDateOrRating')

    model_config = ConfigDict(populate_by_name=True, extra='allow')

    @field_validator('order_by')
    def restrict_sortable_fields(cls, value):  # noqa
        if value is None:
            return None

        allowed_field_names = ['rating', 'visit_date']

        for field_name in value:
            field_name = field_name.replace('+', '').replace('-', '')
            if field_name not in allowed_field_names:
                raise ValueError(f"You may only sort by: {', '.join(allowed_field_names)}")

        return value

    class Constants(Filter.Constants):
        model = Place
