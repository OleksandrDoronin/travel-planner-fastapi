import logging
from typing import Annotated
from urllib.parse import urlencode, urljoin

from fastapi import Depends

from src.auth.constants import GOOGLE_OAUTH_BASE_URL
from src.auth.dependencies import cypher
from src.auth.exceptions import GoogleOAuthError, GoogleOAuthUrlGenerationError
from src.auth.repositories.google_oauth import GoogleOAuthRepository
from src.auth.repositories.social_account import SocialAccountRepository
from src.auth.repositories.user import UserRepository
from src.auth.schemas.auth_schemas import (
    GoogleAuthRequest,
    GoogleLoginResponse,
)
from src.auth.schemas.google_oauth import GoogleTokenResponse, GoogleUserInfoResponse
from src.auth.schemas.user_schemas import (
    SocialAccountLink,
    UserBase,
    UserWithSocialAccountsResponse,
)
from src.auth.utils.security_utils import encode_token
from src.settings import settings


logger = logging.getLogger(__name__)


class GoogleAuthService:
    """
    Service for handling Google OAuth authentication and linking social accounts.
    """

    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        social_repository: Annotated[SocialAccountRepository, Depends(SocialAccountRepository)],
        google_oauth_repo: Annotated[GoogleOAuthRepository, Depends(GoogleOAuthRepository)],
    ):
        self.user_repository = user_repository
        self.social_repository = social_repository
        self.google_oauth_repo = google_oauth_repo

    async def handle_google_callback(
        self, code: str, redirect_uri: str, state: str
    ) -> UserWithSocialAccountsResponse:
        """
        Handles the Google OAuth callback, fetches tokens, user info,
        and connects the account.
        """

        # Validate parameters
        await self._validate_callback_params(code=code, redirect_uri=redirect_uri, state=state)

        # Fetch tokens and user info
        token_data = await self._fetch_google_tokens(code=code, redirect_uri=redirect_uri)
        user_info = await self._fetch_google_user_info(access_token=token_data.access_token)

        # Create or retrieve user, and link social account
        user = await self._create_or_get_user(user_info=user_info)
        await self._create_or_connect_social_account(
            user_info=user_info, token_data=token_data, user_id=user.id
        )

        return await self._prepare_callback_response(user=user)

    @staticmethod
    async def _validate_callback_params(code: str, redirect_uri: str, state: str) -> None:
        """Validate required parameters for the callback."""
        if not all([code, redirect_uri, state]):
            raise GoogleOAuthError()

    async def _create_or_get_user(self, user_info: GoogleUserInfoResponse) -> UserBase:
        """
        Creates a UserBase object from Google data and stores it in the database if necessary.
        """
        user = UserBase(
            email=user_info.email,
            full_name=user_info.name,
            profile_picture=user_info.picture,
        )
        return await self.create_or_get_user(user=user)

    async def create_or_get_user(self, user: UserBase) -> UserBase:
        """
        Creates a new user or retrieves an existing one by email.
        """
        existing_user = await self.user_repository.get_user_by_email(email=user.email)
        if not existing_user:
            return await self.user_repository.create_user(user=user)
        return existing_user

    async def _create_or_connect_social_account(
        self,
        user_info: GoogleUserInfoResponse,
        token_data: GoogleTokenResponse,
        user_id: int,
    ) -> SocialAccountLink:
        """
        Creates or connects a social account based on Google user info and tokens.
        """
        return await self.get_or_connect_accounts(
            user_info=user_info, token_data=token_data, user_id=user_id
        )

    async def get_or_connect_accounts(
        self,
        user_info: GoogleUserInfoResponse,
        token_data: GoogleTokenResponse,
        user_id: int,
    ) -> SocialAccountLink:
        """
        Links a social account to the user or updates an existing one.
        """
        social_account = SocialAccountLink(
            service='google',
            social_account_id=user_info.id,
            access_token=encode_token(token=token_data.access_token, cypher=cypher),
            refresh_token=encode_token(token=token_data.refresh_token, cypher=cypher),
            user_id=user_id,
        )

        existing_account = await self.social_repository.get_social_account(
            social_account=social_account
        )
        if existing_account:
            existing_account.access_token = social_account.access_token
            existing_account.refresh_token = social_account.refresh_token
            return await self.social_repository.update_social_account(
                social_account=existing_account
            )

        return await self.social_repository.create_social_account(social_account=social_account)

    async def _fetch_google_tokens(self, code: str, redirect_uri: str) -> GoogleTokenResponse:
        """
        Fetch tokens from Google and validate the access token.
        """
        return await self.google_oauth_repo.fetch_token(code=code, redirect_uri=redirect_uri)

    async def _fetch_google_user_info(self, access_token: str) -> GoogleUserInfoResponse:
        """
        Fetches user information from Google using the provided access token.
        """
        return await self.google_oauth_repo.fetch_user_info(access_token=access_token)

    async def _prepare_callback_response(self, user: UserBase) -> UserWithSocialAccountsResponse:
        """
        Prepares the response for the Google OAuth callback.
        """
        social_accounts = await self.social_repository.get_social_accounts_for_user(
            user_id=user.id, response_model=SocialAccountLink
        )

        return UserWithSocialAccountsResponse(
            **user.model_dump(),
            social_accounts=social_accounts,
        )


class GoogleOAuthUrlGenerator:
    async def generate_auth_url(self, redirect_uri: str, state: str) -> GoogleLoginResponse:
        """Generate the Google OAuth URL and manage the state."""

        google_auth_url = self._get_google_auth_url(redirect_uri=redirect_uri, state=state)
        if not google_auth_url:
            raise GoogleOAuthUrlGenerationError()

        return GoogleLoginResponse(url=google_auth_url)

    def _get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Helper to generate the Google OAuth URL."""
        google_auth_request = GoogleAuthRequest(redirect_uri=redirect_uri, state=state)

        query_params = self._generate_query_params(google_auth_request)

        auth_url = urljoin(GOOGLE_OAUTH_BASE_URL, '?' + urlencode(query_params))

        return auth_url

    @staticmethod
    def _generate_query_params(google_auth_request: GoogleAuthRequest) -> dict:
        """Helper function to generate the OAuth query parameters."""
        return {
            'response_type': 'code',
            'client_id': settings.google_oauth_key,
            'redirect_uri': google_auth_request.redirect_uri,
            'state': google_auth_request.state,
            'scope': 'email openid profile',
            'access_type': 'offline',
            'prompt': 'consent',
        }
