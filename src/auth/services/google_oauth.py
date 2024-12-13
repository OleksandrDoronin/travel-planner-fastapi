import logging
from typing import Annotated
from urllib.parse import urlencode, urlunparse

from cryptography.fernet import Fernet
from fastapi import Depends

from src.auth.dependencies import get_cypher
from src.auth.exceptions import GoogleOAuthError
from src.auth.repositories.google_oauth import GoogleOAuthRepository
from src.auth.repositories.social_account import SocialAccountRepository
from src.auth.repositories.user import UserRepository
from src.auth.schemas.auth_schemas import (
    GoogleAuthRequest,
    GoogleCallBackResponse,
    GoogleLoginResponse,
)
from src.auth.schemas.google_oauth import GoogleTokenResponse, GoogleUserInfoResponse
from src.auth.schemas.user_schemas import (
    SocialAccountLink,
    UserBase,
    UserWithSocialAccountsResponse,
)
from src.auth.services.token import TokenService
from src.auth.utils import encode_token, generate_random_state
from src.services.cache import CacheService
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
        token_service: Annotated[TokenService, Depends(TokenService)],
        google_oauth_repo: Annotated[GoogleOAuthRepository, Depends(GoogleOAuthRepository)],
        cypher: Annotated[Fernet, Depends(get_cypher)],
        cache_service: Annotated[CacheService, Depends(CacheService)],
    ):
        self._service = 'google'
        self.user_repository = user_repository
        self.social_repository = social_repository
        self.google_oauth_repo = google_oauth_repo
        self.token_service = token_service
        self.cypher = cypher
        self.cache_service = cache_service

    async def handle_google_callback(
        self, code: str, redirect_uri: str, state: str
    ) -> GoogleCallBackResponse:
        """
        Handles the Google OAuth callback, fetches tokens, user info,
        and connects the account.
        """

        # Validate parameters
        await self._validate_callback_params(code=code, redirect_uri=redirect_uri, state=state)

        # Fetch tokens and user info
        token_data = await self._fetch_google_tokens(code=code, redirect_uri=redirect_uri)
        user_info = await self._fetch_google_user_info(access_token=token_data['access_token'])

        # Create or retrieve user, and link social account
        user = await self._create_or_get_user(user_info=user_info)
        await self._create_or_connect_social_account(
            user_info=user_info, token_data=token_data, user_id=user.id
        )

        # Prepare response
        return await self._prepare_callback_response(user=user)

    async def _validate_callback_params(self, code: str, redirect_uri: str, state: str) -> None:
        """Validate required parameters for the callback."""
        if not all([code, redirect_uri, state]):
            raise GoogleOAuthError()

        await self.verify_state(state=state)

    async def _create_or_get_user(self, user_info: GoogleUserInfoResponse) -> UserBase:
        """
        Creates a UserBase object from Google data and stores it in the database if necessary.
        """
        user = UserBase(
            email=user_info['email'],
            full_name=user_info['name'],
            profile_picture=user_info['picture'],
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
            service=self._service,
            social_account_id=user_info['id'],
            access_token=encode_token(token_data['access_token'], self.cypher),
            refresh_token=encode_token(token_data['refresh_token'], self.cypher),
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

    async def _prepare_callback_response(self, user: UserBase) -> GoogleCallBackResponse:
        """
        Prepares the response for the Google OAuth callback.
        """
        social_accounts = await self.social_repository.get_social_accounts_for_user(user_id=user.id)
        access_token = self.token_service.create_access_token(user_id=user.id)
        refresh_token = self.token_service.create_refresh_token(user_id=user.id)

        user_response = UserWithSocialAccountsResponse(
            **user.model_dump(),
            social_accounts=social_accounts,
        )
        return GoogleCallBackResponse(
            user=user_response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def verify_state(self, state: str):
        """Validate that the state matches."""
        cached_state = await self.cache_service.get_cache(f'google_oauth_state_{state}')
        if cached_state is None or cached_state.get('state') != state:
            logger.error('Invalid state parameter. State received: %s', state)
            raise GoogleOAuthError()


class GoogleOAuthUrlGenerator:
    def __init__(
        self,
        cache_service: Annotated[CacheService, Depends(CacheService)],
    ):
        self.cache_service = cache_service

    async def generate_auth_url(self, redirect_uri: str) -> tuple[GoogleLoginResponse, str]:
        """Generate the Google OAuth URL and manage the state."""

        # Generate and store state in cache
        state = await self._generate_and_cache_state()

        google_auth_url = self._get_google_auth_url(redirect_uri=redirect_uri, state=state)
        if not google_auth_url:
            raise ValueError('Failed to generate Google OAuth URL')

        return GoogleLoginResponse(url=google_auth_url), state

    async def _generate_and_cache_state(self) -> str:
        """Generate a random state and save it to cache."""
        state = generate_random_state()
        await self.cache_service.set_cache(f'google_oauth_state_{state}', {'state': state}, ttl=100)
        return state

    def _get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Helper to generate the Google OAuth URL."""
        google_auth_request = GoogleAuthRequest(redirect_uri=redirect_uri, state=state)

        query_params = self._generate_query_params(google_auth_request)

        return urlunparse(
            (
                'https',
                'accounts.google.com',
                '/o/oauth2/v2/auth',
                '',
                urlencode(query_params),
                '',
            )
        )

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
