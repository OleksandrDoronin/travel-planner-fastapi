import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from fastapi.params import Depends
from fastapi_filter import FilterDepends
from starlette import status

from src.auth.current_user import get_current_user
from src.dependencies import get_pagination_params
from src.models import User
from src.pagination import PaginationParams
from src.places.exceptions import (
    GeoServiceError,
    LocationValidationError,
    PlaceAlreadyExistsError,
    PlaceError,
    PlaceNotFoundError,
)
from src.places.schemas.filters import PlaceFilter
from src.places.schemas.places import PlaceCreationRequest, PlaceResponse, PlaceUpdateRequest
from src.places.services.places import PlaceService


router = APIRouter(tags=['place'], prefix='/places')
logger = logging.getLogger(__name__)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=PlaceResponse,
    summary='Create a new place',
)
async def create_place(
    place_data: Annotated[PlaceCreationRequest, Body(...)],
    places_services: Annotated[PlaceService, Depends(PlaceService)],
    current_user: User = Depends(get_current_user),
):
    try:
        place = await places_services.create_place(user_id=current_user.id, place_data=place_data)
        return place

    except (PlaceAlreadyExistsError, LocationValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    except GeoServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )

    except PlaceError as e:
        logger.exception('Place error occurred while creating a place.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=list[PlaceResponse],
    summary='Get a list of all places',
)
async def get_places(
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    place_filter: Annotated[PlaceFilter, FilterDepends(PlaceFilter)],
):
    try:
        return await place_service.get_places(
            user_id=current_user.id,
            filters=place_filter,
            offset=pagination.offset,
            limit=pagination.limit,
        )

    except PlaceNotFoundError as e:
        logger.exception('Place not found while retrieving places.')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    except PlaceError as e:
        logger.exception('Place error occurred while retrieving places.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


@router.get(
    '/{place_id}',
    status_code=status.HTTP_200_OK,
    response_model=PlaceResponse,
    summary='Retrieve a specific place by ID',
)
async def get_place_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    place_id: int,
):
    try:
        return await place_service.get_place_by_id(place_id=place_id, user_id=current_user.id)

    except PlaceNotFoundError as e:
        logger.exception(f'Place with ID {place_id} not found.')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    except PlaceError as e:
        logger.exception('Place error occurred while retrieving place by ID.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


@router.put(
    '/{place_id}',
    status_code=status.HTTP_200_OK,
    response_model=PlaceResponse,
    summary='Update a specific place by ID',
)
async def update_place_by_id(
    place_data: Annotated[PlaceUpdateRequest, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    place_id: int,
):
    try:
        updated_place = await place_service.update_place_by_id(
            place_id=place_id, user_id=current_user.id, place_data=place_data
        )
        return updated_place

    except PlaceNotFoundError as e:
        logger.exception(f'Place with ID {place_id} not found for update.')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    except LocationValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    except PlaceError as e:
        logger.exception('Place error occurred while updating the place.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


@router.delete(
    '/{place_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete place by id',
)
async def delete_place_by_id(
    place_service: Annotated[PlaceService, Depends(PlaceService)],
    current_user: Annotated[User, Depends(get_current_user)],
    place_id: int,
):
    try:
        await place_service.delete_place_by_id(place_id=place_id, user_id=current_user.id)

    except PlaceNotFoundError as e:
        logger.exception(f'Place with ID {place_id} not found for deletion.')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    except PlaceError as e:
        logger.exception('Place error occurred while deleting the place.')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
