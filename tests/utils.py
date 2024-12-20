from datetime import datetime, timedelta, timezone

from jose import jwt

from src.settings import settings


def create_test_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=1)
    to_encode = {'sub': str(user_id), 'exp': expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)
    return encoded_jwt
