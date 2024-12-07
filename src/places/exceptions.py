class LocationValidationError(Exception):
    """Exception raised when location validation fails."""

    def __init__(self, city: str, country: str):
        self.city = city
        self.country = country
        self.message = f'Invalid location: {city}, {country}'
        super().__init__(self.message)


class PlaceAlreadyExistsError(Exception):
    """Exception raised when the place already exists for the user."""

    def __init__(self, place_name: str, city: str, place_type: str):
        self.place_name = place_name
        self.city = city
        self.place_type = place_type
        self.message = (
            f'The place "{place_name}" in city "{city}" with type '
            f'"{place_type}" already exists for this user.'
        )
        super().__init__(self.message)


class GeoServiceError(Exception):
    """Exception raised when there is a geo service error."""

    def __init__(self, message='Geo service error occurred. Please try again later.'):
        self.message = message
        super().__init__(self.message)
