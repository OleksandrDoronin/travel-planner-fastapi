import logging
from typing import Annotated
from urllib.parse import urlencode, urlunparse

from cryptography.fernet import Fernet
from fastapi import Depends

from src.auth.dependencies import get_cypher
from src.auth.mapper import map_and_encode_tokens, map_to_user
from src.auth.repositories.google_oauth import GoogleOAuthRepository
from src.auth.repositories.social_account import SocialAccountRepository
from src.auth.repositories.user import UserRepository
from src.auth.schemas.auth_schemas import (
    GoogleAuthRequestSchema,
    GoogleCallBackResponse,
    GoogleLoginResponse,
)
from src.auth.schemas.user_schemas import SocialAccountLink, UserBase, UserResponse
from src.auth.services.token import TokenService
from src.auth.utils import generate_random_state
from src.services.cache import CacheService
from src.settings import Settings, get_settings


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
        google_oauth_repo: Annotated[
            GoogleOAuthRepository, Depends(GoogleOAuthRepository)
        ],
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

        # Check that all necessary parameters are present
        await self.validate_required_params(
            code=code, redirect_uri=redirect_uri, state=state
        )

        # Check that the state from the cache matches the one sent
        await self.verify_state(state=state)

        # Fetch tokens and user info
        token_data = await self._fetch_and_validate_google_tokens(
            code=code, redirect_uri=redirect_uri
        )

        # Get user information from Google using an access token
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

    async def _fetch_and_validate_google_tokens(
        self, code: str, redirect_uri: str
    ) -> dict:
        """
        Fetch tokens from Google and validate the access token.
        """
        token_data = await self.google_oauth_repo.fetch_token(
            code=code, redirect_uri=redirect_uri
        )

        # Validate access token
        if 'access_token' not in token_data:
            raise ValueError('Access token not found in response')

        return token_data

    async def _fetch_google_user_info(self, access_token: str):
        """
        Fetches user information from Google using the provided access token.
        """
        return await self.google_oauth_repo.fetch_user_info(access_token=access_token)

    def _map_social_account(self, user_info, token_data, user_id):
        """
        Maps the Google user info and tokens to a social account object.
        """
        if 'id' not in user_info:
            raise ValueError('Missing "id" in user info from Google.')

        return map_and_encode_tokens(
            service=self._service,
            social_account_id=user_info['id'],
            tokens=token_data,
            user_id=user_id,
            encryptor=self.cypher,
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

    async def verify_state(self, state: str):
        """Validate that the state matches."""
        cached_state = await self.cache_service.get_cache(f'google_oauth_state_{state}')
        if cached_state is None or cached_state.get('state') != state:
            raise ValueError('Invalid state parameter.')

    @staticmethod
    async def validate_required_params(code, redirect_uri, state):
        """Validate that the authorization code, redirect URI, and state are present."""
        if not code or not redirect_uri or not state:
            raise ValueError(
                'Authorization code, redirect URI, and state are required.'
            )


class GoogleOAuthUrlGenerator:
    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        cache_service: Annotated[CacheService, Depends(CacheService)],
    ):
        self.settings = settings
        self.cache_service = cache_service

    async def generate_auth_url(
        self, redirect_uri: str
    ) -> tuple[GoogleLoginResponse, str]:
        """Generate the Google OAuth URL and manage the state."""

        # Generate and store state in cache
        state = await self._generate_and_cache_state()

        google_auth_url = self._get_google_auth_url(
            redirect_uri=redirect_uri, state=state
        )
        if not google_auth_url:
            raise ValueError('Failed to generate Google OAuth URL')

        return GoogleLoginResponse(url=google_auth_url), state

    async def _generate_and_cache_state(self) -> str:
        """Generate a random state and save it to cache."""
        state = generate_random_state()
        await self.cache_service.set_cache(
            f'google_oauth_state_{state}', {'state': state}, ttl=100
        )
        return state

    def _get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Helper to generate the Google OAuth URL."""
        google_auth_request = GoogleAuthRequestSchema(
            redirect_uri=redirect_uri, state=state
        )

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

    def _generate_query_params(
        self, google_auth_request: GoogleAuthRequestSchema
    ) -> dict:
        """Helper function to generate the OAuth query parameters."""
        return {
            'response_type': 'code',
            'client_id': self.settings.GOOGLE_OAUTH_KEY,
            'redirect_uri': google_auth_request.redirect_uri,
            'state': google_auth_request.state,
            'scope': 'email openid profile',
            'access_type': 'offline',
            'prompt': 'consent',
        }
