from datetime import datetime

from cryptography.fernet import Fernet

from src.auth.schemas.auth_schemas import TokenBlacklistSchema
from src.auth.schemas.user_schemas import SocialAccountLink, UserBase
from src.auth.utils import encode_token


def map_to_user(user: dict) -> UserBase:
    return UserBase(
        email=user['email'],
        full_name=user['name'],
        profile_picture=user['picture'],
    )


def map_and_encode_tokens(
    service: str, social_account_id: str, tokens: dict, user_id: int, encryptor: Fernet
) -> SocialAccountLink:
    return SocialAccountLink(
        service=service,
        social_account_id=social_account_id,
        access_token=encode_token(tokens['access_token'], encryptor),
        refresh_token=encode_token(tokens['refresh_token'], encryptor),
        user_id=user_id,
    )


def map_refresh_token(token: str, expires_at: datetime) -> TokenBlacklistSchema:
    return TokenBlacklistSchema(token=token, expires_at=expires_at)
