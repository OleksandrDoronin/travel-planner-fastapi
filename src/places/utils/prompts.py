def generate_description_prompt(place_name: str, city: str, country: str) -> str:
    return (
        f"Provide a brief description of the place named '{place_name}' "
        f'located in {city}, {country}. Additionally, please find a working URL to a '
        f'photo of this place.'
    )
