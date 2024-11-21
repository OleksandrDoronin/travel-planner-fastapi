from enum import Enum


class PlaceRating(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class PlaceType(str, Enum):
    VISITED = 'visited'
    FAVORITE = 'favorite'


class PlannedPlaceStatus(str, Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
