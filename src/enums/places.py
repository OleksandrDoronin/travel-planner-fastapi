from enum import Enum


class PlaceRating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class PlaceType(Enum):
    VISITED = 'visited'
    FAVORITE = 'favorite'
