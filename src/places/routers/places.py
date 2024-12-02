import logging
from typing import Annotated, List

from auth.security import get_current_user
from fastapi import APIRouter, Body, HTTPException
from fastapi.params import Depends
from models import User
from places.schemas.places import PlaceCreate, PlaceGet
from places.services.places import PlaceService
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
async def create_place(
    place_data: Annotated[PlaceCreate, Body(...)],
    places_services: Annotated[PlaceService, Depends(PlaceService)],
    current_user: User = Depends(get_current_user),
):
    try:
        place = await places_services.create_place(
            user_id=current_user.id, place_data=place_data
        )
        return place

    except ValueError as e:
        logger.error(f'Value error: {repr(e)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except RuntimeError as e:
        logger.error(f'RuntimeError: {repr(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    except Exception as e:
        logger.critical(f'Unexpected error: {repr(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error',
        )


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=List[PlaceGet],
    summary='Get a list of all places',
)
async def get_places(
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await place_service.get_places(user_id=current_user.id)

    except ValueError as e:
        logger.error(f'Value error: {repr(e)}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.critical(f'Unexpected error: {repr(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to fetch places.',
        )


@router.get(
    '/{place_id}',
    status_code=status.HTTP_200_OK,
    response_model=PlaceGet,
    summary='Retrieve a specific place by ID',
)
async def get_place_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    place_id: int,
):
    try:
        return await place_service.get_place_by_id(
            place_id=place_id, user_id=current_user.id
        )

    except ValueError as e:
        logger.error(f'Value error: {repr(e)}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.critical(f'Unexpected error: {repr(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to fetch places.',
        )
