from typing import Annotated

from cryptography.fernet import Fernet
from fastapi.params import Depends

from src.auth.dependencies import get_cypher


class Encoder:
    """
    Simple class to encode and decode tokens.
    """

    def __init__(self, cypher: Annotated[Fernet, Depends(get_cypher)]):
        self.cypher = cypher

    def encode(self, token: str) -> str:
        return self.cypher.encrypt(token.encode()).decode()

    def decode(self, token: str) -> str:
        return self.cypher.decrypt(token.encode()).decode()
