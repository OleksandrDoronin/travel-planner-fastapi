def generate_description_prompt(place_name: str, city: str, country: str) -> str:
    return (
        f'Provide a brief description of the '
        f"place named '{place_name}' located in {city}, {country}."
    )
