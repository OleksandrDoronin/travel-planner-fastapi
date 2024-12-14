import logging
from string import Template

from src.auth.constants import CACHE_TTL, GOOGLE_STATE_TEMPLATE
from src.auth.exceptions import GoogleOAuthError
from src.auth.utils.security_utils import generate_random_state
from src.services.cache import CacheService


logger = logging.getLogger(__name__)


async def generate_and_cache_state(cache_service: CacheService) -> str:
    """Generate a random state and save it to cache."""
    state = generate_random_state()

    # Generate a key for the cache
    cache_key_template = Template(GOOGLE_STATE_TEMPLATE)
    cache_key = cache_key_template.substitute(state=state)

    # Saving state to cache
    await cache_service.set_cache(cache_key, {'state': state}, ttl=CACHE_TTL)

    return state


async def verify_state(cache_service: CacheService, state: str) -> dict[str, str]:
    """Validate that the state matches."""
    cached_state = await cache_service.get_cache(f'google_oauth_state_{state}')
    if cached_state is None or cached_state.get('state') != state:
        logger.error('Invalid state parameter. State received: %s', state)
        raise GoogleOAuthError()

    return cached_state
