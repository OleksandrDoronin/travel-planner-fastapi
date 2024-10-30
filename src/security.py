from datetime import datetime, timezone
from datetime import timedelta
from typing import Optional
import jwt
from fastapi.security import OAuth2PasswordBearer
import logging
from passlib.context import CryptContext

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("passlib")
logger.setLevel(logging.ERROR)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")


def get_password_hash(password: str) -> str:
    """Hashes a plain text password using the bcrypt algorithm."""
    return bcrypt_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Password verification"""
    return bcrypt_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode["id"] = data.get("id")
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
