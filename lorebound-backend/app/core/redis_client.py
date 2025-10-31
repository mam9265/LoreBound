"""Redis client for caching and pub/sub."""

import json
from typing import Optional, Any
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from .config import settings


class RedisClient:
    """Redis client wrapper for async operations."""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Initialize Redis connection."""
        if not self._redis:
            self._redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
            )
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._redis:
            await self.connect()
        return await self._redis.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: Optional[int] = None
    ) -> None:
        """Set value in Redis with optional expiration."""
        if not self._redis:
            await self.connect()
        await self._redis.set(key, value, ex=expire_seconds)
    
    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        if not self._redis:
            await self.connect()
        await self._redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._redis:
            await self.connect()
        return await self._redis.exists(key) > 0
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis."""
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None
    ) -> None:
        """Set JSON value in Redis with optional expiration."""
        json_str = json.dumps(value, default=str)
        await self.set(key, json_str, expire_seconds)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in Redis."""
        if not self._redis:
            await self.connect()
        return await self._redis.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> None:
        """Set expiration on existing key."""
        if not self._redis:
            await self.connect()
        await self._redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get time-to-live for key."""
        if not self._redis:
            await self.connect()
        return await self._redis.ttl(key)
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self._redis:
            await self.connect()
        
        # Use SCAN to find keys matching pattern
        deleted_count = 0
        cursor = 0
        
        while True:
            cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
            if keys:
                deleted_count += await self._redis.delete(*keys)
            if cursor == 0:
                break
        
        return deleted_count


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency function to get Redis client."""
    if not redis_client._redis:
        await redis_client.connect()
    return redis_client


@asynccontextmanager
async def redis_context():
    """Context manager for Redis operations."""
    client = RedisClient()
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()

