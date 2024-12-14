import logging
from typing import Annotated

from fastapi import Depends

from src.auth.repositories.social_account import SocialAccountRepository
from src.auth.repositories.user import UserRepository
from src.auth.schemas.user_schemas import ExtendedUserResponse, SocialAccountResponse


logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        social_repository: Annotated[SocialAccountRepository, Depends(SocialAccountRepository)],
    ):
        self.user_repository = user_repository
        self.social_repository = social_repository

    async def get_user_by_id(self, user_id: int) -> ExtendedUserResponse:
        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if not user:
            raise ValueError('User not found')

        social_accounts = await self.social_repository.get_social_accounts_for_user(
            user_id=user.id, response_model=SocialAccountResponse
        )

        user_response = ExtendedUserResponse(**user.model_dump(), social_accounts=social_accounts)
        return user_response
