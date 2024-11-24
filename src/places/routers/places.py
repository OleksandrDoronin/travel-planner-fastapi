import logging
from typing import List

from fastapi import APIRouter
from places.schemas.places import PlaceGet
from settings import get_settings
from starlette import status


router = APIRouter(tags=['place'], prefix='/places')
logger = logging.getLogger('travel_planner_app')
settings = get_settings()


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=PlaceGet,
    summary='Create a new place',
)
async def create_place():
    pass


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=List[PlaceGet],
    summary='Get a list of all places',
)
async def get_places():
    pass


@router.get(
    '/{place_id}',
    status_code=status.HTTP_200_OK,
    response_model=PlaceGet,
    summary='Retrieve a specific place by ID',
)
async def get_place_by_id(place_id: int):
    pass
