from passlib.context import CryptContext


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashes a plain text password using the bcrypt algorithm."""
    return bcrypt_context.hash(password)


def verify_password(password, hashed_password) -> bool:
    """Password verification"""
    return bcrypt_context.verify(password, hashed_password)
