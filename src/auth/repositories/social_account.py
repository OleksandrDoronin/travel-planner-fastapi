import logging
from typing import Annotated, Type

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import GoogleOAuthError
from src.auth.schemas.user_schemas import SocialAccountLink, SocialAccountResponse
from src.dependencies import get_db
from src.models.social_account import SocialAccount


logger = logging.getLogger(__name__)


class SocialAccountRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def create_social_account(self, social_account: SocialAccountLink) -> SocialAccountLink:
        """
        Creates a new social account in the database and returns the validated model.
        """
        try:
            social_account = SocialAccount(**social_account.model_dump())

            self.db_session.add(social_account)
            await self.db_session.commit()
            await self.db_session.refresh(social_account)

            return SocialAccountLink.model_validate(social_account)

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to create social account for: {str(e)}')
            raise GoogleOAuthError()

    async def update_social_account(self, social_account: SocialAccountLink) -> SocialAccountLink:
        """
        Updates an existing social account in the database and returns the
        validated model.
        """
        try:
            result = await self.db_session.execute(
                select(SocialAccount).filter_by(id=social_account.id)
            )

            entity = result.scalar_one()
            entity.access_token = social_account.access_token
            entity.refresh_token = social_account.refresh_token

            await self.db_session.commit()

            return SocialAccountLink.model_validate(social_account)

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f'Failed to update social account for: {str(e)}')
            raise GoogleOAuthError()

    async def get_social_accounts_for_user(
        self, user_id: int, response_model: Type[SocialAccountLink | SocialAccountResponse]
    ) -> list[SocialAccountLink] | list[SocialAccountResponse]:
        """
        Fetches all social accounts associated with the user and returns validated models.
        Optionally returns response models if response_model is True.
        """

        try:
            result = await self.db_session.execute(
                select(SocialAccount).where(SocialAccount.user_id == user_id)
            )
            social_accounts = result.scalars().all()

            return [response_model.model_validate(account) for account in social_accounts]

        except SQLAlchemyError as e:
            logger.error(f'Failed to get social accounts for user {user_id}: {str(e)}')
            raise GoogleOAuthError()

    async def get_social_account(self, social_account: SocialAccountLink) -> SocialAccountLink:
        """
        Fetches a specific social account by service and social account ID
        and returns the validated model.
        """
        try:
            result = await self.db_session.execute(
                select(SocialAccount).where(
                    SocialAccount.service == social_account.service,
                    SocialAccount.social_account_id == social_account.social_account_id,
                )
            )
            social_account = result.scalars().first()

            return (
                SocialAccountLink.model_validate(social_account)
                if social_account is not None
                else None
            )

        except SQLAlchemyError as e:
            logger.error(f'Failed to get social account for: {str(e)}')
            raise GoogleOAuthError()
