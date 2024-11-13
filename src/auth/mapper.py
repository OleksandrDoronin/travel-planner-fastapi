from auth.schemas.user_schemas import SocialAccountLink, UserBase
from auth.services.encoder import Encoder


def map_to_user(user: dict) -> UserBase:
    return UserBase(
        email=user['email'],
        full_name=user['name'],
        avatar=user['picture'],
        username=user['email'].split('@')[0],
    )


def map_and_encode_tokens(
    service: str, social_account_id: str, tokens: dict, user_id: int, encryptor: Encoder
) -> SocialAccountLink:
    return SocialAccountLink(
        service=service,
        social_account_id=social_account_id,
        access_token=encryptor.encode(tokens['access_token']),
        refresh_token=encryptor.encode(tokens['refresh_token']),
        user_id=user_id,
    )
