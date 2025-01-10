from pydantic import BaseModel


class PlaceInfoRequest(BaseModel):
    place_name: str
    city: str | None = None
    country: str | None = None


class PlaceDetailResponse(BaseModel):
    description: str
    photo_url: str
