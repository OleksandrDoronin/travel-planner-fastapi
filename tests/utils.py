import base64
import json

from settings import get_settings


settings = get_settings()


def extract_session_state(session_cookie):
    if session_cookie:
        session_state_json = base64.b64decode(session_cookie).decode('utf-8')
        session_state_dict = json.loads(session_state_json)
        return session_state_dict.get('state')
    return None
