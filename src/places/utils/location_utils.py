from string import Template

from src.places.constants import PLACES_CACHE_KEY


def generate_cache_key(city: str, country: str) -> str:
    """
    Generates a cache key for location data based on city and country.
    """
    cache_key_template = Template(template=PLACES_CACHE_KEY)

    return cache_key_template.substitute(city=city, country=country)


def format_location(city: str, country: str) -> tuple[str, str]:
    """
    Formats the city and country into title case.
    """
    formatted_city = city.strip().title()
    formatted_country = country.strip().title()

    return formatted_city, formatted_country


def is_location_valid(components: dict[str, str], city: str, country: str) -> bool:
    """
    Checks if the API response matches the provided city and country.
    """
    return (
        components.get('city', '').lower() == city.lower()
        and components.get('country', '').lower() == country.lower()
    )
