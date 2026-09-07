"""
api/cache/redis_client.py
Asynchronous Redis caching layer with in-memory fallback.
"""

import functools
import json
import logging
import os
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages Redis connection with in-memory TTL fallback."""
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        self._redis = None
        self._memory_cache: Dict[str, tuple[Any, float]] = {}

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self._redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=2.0
            )
            await self._redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Using in-memory cache fallback.")
            self._redis = None

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[str]:
        if self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        
        # Memory fallback
        if key in self._memory_cache:
            val, expiry = self._memory_cache[key]
            if time.time() < expiry:
                return val
            del self._memory_cache[key]
        return None

    async def setex(self, key: str, ttl_seconds: int, value: str):
        if self._redis:
            try:
                await self._redis.setex(key, ttl_seconds, value)
                return
            except Exception:
                pass
        self._memory_cache[key] = (value, time.time() + ttl_seconds)

    async def flush(self):
        if self._redis:
            try:
                await self._redis.flushdb()
            except Exception:
                pass
        self._memory_cache.clear()

cache = CacheManager()
