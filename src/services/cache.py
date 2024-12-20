import json
import logging

import redis.asyncio as redis

from src.settings import settings


logger = logging.getLogger(__name__)


redis_client = redis.from_url(settings.redis_url)


class CacheService:
    @staticmethod
    async def get_cache(key: str) -> dict | None:
        try:
            cached_data = await redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f'Unexpected error while retrieving data from Redis: {e}')
        return None

    @staticmethod
    async def set_cache(key: str, value: dict, ttl: int = 3600) -> None:
        try:
            await redis_client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f'Unexpected error while setting data to Redis: {e}')

    @staticmethod
    async def check_connection() -> bool:
        """
        Check connection to Redis.
        """
        try:
            pong = await redis_client.ping()
            if pong:
                logger.info('Successfully connected to Redis.')
                return True
            else:
                logger.error('Failed to connect to Redis.')
                return False
        except Exception as e:
            logger.error(f'Error while connecting to Redis: {e}')
            return False
