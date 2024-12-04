from typing import Annotated

from auth.schemas.user_schemas import SocialAccountLink, SocialAccountResponse
from config.database import get_db
from fastapi import Depends
from models.users import SocialAccount
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SocialAccountRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db)]):
        self.db_session = db_session

    async def create_social_account(
        self, social_account: SocialAccountLink
    ) -> SocialAccountLink:
        """
        Creates a new social account in the database and returns the validated model.
        """

        social_account = SocialAccount(**social_account.model_dump())
        self.db_session.add(social_account)
        await self.db_session.commit()
        await self.db_session.refresh(social_account)
        return SocialAccountLink.model_validate(social_account)

    async def update_social_account(
        self, social_account: SocialAccountLink
    ) -> SocialAccountLink:
        """
        Updates an existing social account in the database and returns the
        validated model.
        """

        result = await self.db_session.execute(
            select(SocialAccount).filter_by(id=social_account.id)
        )
        entity = result.scalar_one()
        entity.access_token = social_account.access_token
        entity.refresh_token = social_account.refresh_token
        await self.db_session.commit()
        return SocialAccountLink.model_validate(social_account)

    async def get_social_accounts_for_user(self, user_id: int):
        """
        Fetches all social accounts associated with the user
        and returns validated models.
        """

        result = await self.db_session.execute(
            select(SocialAccount).where(SocialAccount.user_id == user_id)
        )
        social_accounts = result.scalars().all()
        return [
            SocialAccountLink.model_validate(account) for account in social_accounts
        ]

    async def get_social_account(
        self, social_account: SocialAccountLink
    ) -> SocialAccountLink:
        """
        Fetches a specific social account by service and social account ID
        and returns the validated model.
        """

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

    async def get_social_accounts_for_user_response(self, user_id: int):
        """
        Fetches all social accounts for a user and returns
        them as validated response models.
        """

        result = await self.db_session.execute(
            select(SocialAccount).where(SocialAccount.user_id == user_id)
        )
        social_accounts = result.scalars().all()
        return [
            SocialAccountResponse.model_validate(account) for account in social_accounts
        ]
