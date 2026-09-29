import os
import time
import logging
from typing import Optional, Any

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger("redis_client")

REDIS_URL = os.getenv("REDIS_URL", "").strip()

class ResilientRedisClient:
    """
    Resilient Redis client proxy with in-memory TTL fallback.
    Ensures that if Redis is unavailable, uninstalled, or not provisioned (e.g. Render standard web service),
    the backend continues running with zero downtime and no 500 crashes.
    """
    def __init__(self, redis_url: str):
        self._url = redis_url
        self._real_client = None
        self._redis_available = bool(redis_url and redis is not None)
        self._warned = False
        self._store = {}
        self._expiry = {}

        if self._redis_available:
            try:
                self._real_client = redis.from_url(self._url, decode_responses=True)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client from URL: {e}. Using in-memory fallback.")
                self._redis_available = False

    def _purge_expired(self, key: str):
        if key in self._expiry and time.time() > self._expiry[key]:
            self._store.pop(key, None)
            self._expiry.pop(key, None)

    async def get(self, key: str) -> Optional[str]:
        if self._real_client and self._redis_available:
            try:
                return await self._real_client.get(key)
            except Exception as e:
                if not self._warned:
                    logger.info(f"Redis unavailable ({e}). Falling back to in-memory cache.")
                    self._warned = True
                self._redis_available = False

        self._purge_expired(key)
        return self._store.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        val_str = str(value) if not isinstance(value, (str, bytes)) else value
        if isinstance(val_str, bytes):
            val_str = val_str.decode("utf-8")

        if self._real_client and self._redis_available:
            try:
                return await self._real_client.set(key, val_str, ex=ex)
            except Exception as e:
                if not self._warned:
                    logger.info(f"Redis unavailable ({e}). Falling back to in-memory cache.")
                    self._warned = True
                self._redis_available = False

        self._store[key] = val_str
        if ex:
            self._expiry[key] = time.time() + ex
        else:
            self._expiry.pop(key, None)
        return True

    async def setex(self, key: str, time_secs: int, value: Any) -> bool:
        return await self.set(key, value, ex=time_secs)

    async def delete(self, key: str) -> bool:
        if self._real_client and self._redis_available:
            try:
                await self._real_client.delete(key)
            except Exception:
                self._redis_available = False

        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return True

    async def keys(self, pattern: str = "*") -> list:
        if self._real_client and self._redis_available:
            try:
                return await self._real_client.keys(pattern)
            except Exception:
                self._redis_available = False

        now = time.time()
        valid_keys = [k for k, exp in self._expiry.items() if exp > now]
        return [k for k in self._store.keys() if k in valid_keys or k not in self._expiry]

redis_client = ResilientRedisClient(REDIS_URL)

async def set_session(session_id: str, user_id: int):
    await redis_client.set(f"session:{session_id}", user_id, ex=86400) # 1 day

async def get_session(session_id: str) -> Optional[int]:
    user_id = await redis_client.get(f"session:{session_id}")
    return int(user_id) if user_id else None

async def delete_session(session_id: str):
    await redis_client.delete(f"session:{session_id}")
