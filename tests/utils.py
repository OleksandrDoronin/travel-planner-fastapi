import base64
import json
from datetime import datetime, timedelta, timezone

from jose import jwt

from src.settings import get_settings


settings = get_settings()


def extract_session_state(session_cookie):
    if session_cookie:
        session_state_json = base64.b64decode(session_cookie).decode('utf-8')
        session_state_dict = json.loads(session_state_json)
        return session_state_dict.get('state')
    return None


def create_test_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=1)
    to_encode = {'sub': str(user_id), 'exp': expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
