import random
import string


def generate_random_state(length=16) -> str:
    """Generates a random state to protect against CSRF."""
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
