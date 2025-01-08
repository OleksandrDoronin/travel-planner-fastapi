from pydantic import BaseModel


class DescriptionRequest(BaseModel):
    place_name: str
    city: str | None = None
    country: str | None = None


class DescriptionResponse(BaseModel):
    description: str
