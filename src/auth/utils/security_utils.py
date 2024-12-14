import random
import string

from cryptography.fernet import Fernet


def generate_random_state(length=16) -> str:
    """Generates a random state to protect against CSRF."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def encode_token(token: str, cypher: Fernet) -> str:
    """
    Encodes the token using the provided cypher.
    """
    return cypher.encrypt(token.encode()).decode()


def decode_token(token: str, cypher: Fernet) -> str:
    """
    Decodes the token using the provided cypher.
    """
    return cypher.decrypt(token.encode()).decode()
