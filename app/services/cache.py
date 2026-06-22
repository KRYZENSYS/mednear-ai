"""Cache service for Redis."""

import json
from typing import Any, Optional

from app.config import settings
from app.utils.logger import logger


class CacheService:
    """Async cache service using Redis.

    Provides key-value caching with TTL support and JSON serialization.
    """

    def __init__(self) -> None:
        """Initialize cache service."""
        self._client: Any = None
        self._connected: bool = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(
                settings.redis.url,
                password=settings.redis.password,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Redis cache connected")
        except ImportError:
            logger.warning("redis library not available")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            try:
                await self._client.close()
                self._connected = False
                logger.info("Redis disconnected")
            except Exception as e:
                logger.warning(f"Redis disconnect error: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None.
        """
        if not self._connected:
            return None
        try:
            value = await self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds.

        Returns:
            True if successful.
        """
        if not self._connected:
            return False
        try:
            serialized = json.dumps(value, default=str)
            await self._client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key.

        Returns:
            True if deleted.
        """
        if not self._connected:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Glob pattern (e.g., "user:*").

        Returns:
            Number of keys deleted.
        """
        if not self._connected:
            return 0
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self._client.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.warning(f"Cache clear_pattern error for {pattern}: {e}")
            return 0


cache_service = CacheService()