import logging
from typing import Annotated

from auth.mapper import map_and_encode_tokens, map_to_user
from auth.repositories.social_account import SocialAccountRepository
from auth.repositories.user import UserRepository
from auth.schemas.auth_schemas import GoogleCallBackResponse
from auth.schemas.user_schemas import SocialAccountLink, UserBase, UserResponse
from auth.services.encoder import Encoder
from auth.services.google_oauth_client import GoogleOAuthClient
from auth.services.token import TokenService
from fastapi import Depends


logger = logging.getLogger('travel_planner_app')


class GoogleAuthService:
    """
    Service for handling Google OAuth authentication and linking social accounts.
    """

    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        social_repository: Annotated[
            SocialAccountRepository, Depends(SocialAccountRepository)
        ],
        token_service: Annotated[TokenService, Depends(TokenService)],
        google_oauth_client: Annotated[GoogleOAuthClient, Depends(GoogleOAuthClient)],
        encoder: Annotated[Encoder, Depends(Encoder)],
    ):
        self._service = 'google'
        self.user_repository = user_repository
        self.social_repository = social_repository
        self.google_oauth_client = google_oauth_client
        self.token_service = token_service
        self.encoder = encoder

    async def handle_google_callback(
        self, code: str, redirect_uri: str, state: str, session_state: str
    ) -> GoogleCallBackResponse:
        """
        Handles the Google OAuth callback, fetches tokens, user info,
        and connects the account.
        """

        if not code:
            raise ValueError('Authorization code is required.')

        if session_state != state:
            raise ValueError('Invalid state parameter.')

        try:
            # Fetch tokens and user info
            token_data = await self._fetch_google_tokens(
                code=code, redirect_uri=redirect_uri
            )
            if 'access_token' not in token_data:
                logger.error('No access token received from Google.')
                raise ValueError('Google did not return an access token.')

            user_info = await self._fetch_google_user_info(
                access_token=token_data['access_token']
            )

            # Map to internal user model and create or fetch user
            user = map_to_user(user=user_info)
            user = await self.create_or_get_user(user=user)

            # Create or connect social account
            account = self._map_social_account(
                user_info=user_info, token_data=token_data, user_id=user.id
            )
            await self.get_or_connect_accounts(account=account)

            # Prepare and return response
            return await self._prepare_callback_response(user=user)

        except ValueError as e:
            logger.error(f'Error handling Google callback: {repr(e)}')
            raise

        except Exception as e:
            logger.error(
                'An error occurred while handling Google callback: %s', repr(e)
            )
            raise

    async def create_or_get_user(self, user: UserBase) -> UserBase:
        """
        Creates a new user or retrieves an existing one by email.
        """
        entity = await self.user_repository.get_user_by_email(email=user.email)
        if not entity:
            entity = await self.user_repository.create_user(user=user)
        return entity

    async def get_or_connect_accounts(self, account: SocialAccountLink):
        """
        Links a social account to the user or updates an existing one.
        """
        social_account = await self.social_repository.get_social_account(
            social_account=account
        )
        if not social_account:
            await self.social_repository.create_social_account(social_account=account)
        else:
            social_account.access_token = account.access_token
            social_account.refresh_token = account.refresh_token
            social_account = await self.social_repository.update_social_account(
                social_account=social_account
            )
        return social_account

    async def _fetch_google_tokens(self, code: str, redirect_uri: str):
        """
        Fetches Google OAuth tokens using the provided authorization code.
        """
        return await self.google_oauth_client.fetch_token(
            code=code, redirect_uri=redirect_uri
        )

    async def _fetch_google_user_info(self, access_token: str):
        """
        Fetches user information from Google using the provided access token.
        """
        return await self.google_oauth_client.fetch_user_info(access_token=access_token)

    def _map_social_account(self, user_info, token_data, user_id):
        """
        Maps the Google user info and tokens to a social account object.
        """
        return map_and_encode_tokens(
            service=self._service,
            social_account_id=user_info['id'],
            tokens=token_data,
            user_id=user_id,
            encryptor=self.encoder,
        )

    async def _prepare_callback_response(
        self, user: UserBase
    ) -> GoogleCallBackResponse:
        """
        Prepares the response for the Google OAuth callback.
        """
        social_accounts = await self.social_repository.get_social_accounts_for_user(
            user_id=user.id
        )
        access_token = self.token_service.create_access_token(user_id=user.id)
        refresh_token = self.token_service.create_refresh_token(user_id=user.id)

        user_response = UserResponse(
            **user.model_dump(),
            social_accounts=social_accounts,
        )
        return GoogleCallBackResponse(
            user=user_response,
            access_token=access_token,
            refresh_token=refresh_token,
        )
