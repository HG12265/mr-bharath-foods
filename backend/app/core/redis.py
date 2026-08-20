
import time
from collections.abc import Mapping
from typing import Any
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger


class MockPipeline:
    def __init__(self, client: "MockRedis"):
        self.client = client
        self.commands: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def zremrangebyscore(self, key: str, min_val: Any, max_val: Any) -> "MockPipeline":
        self.commands.append(("zremrangebyscore", (key, min_val, max_val), {}))
        return self

    def zadd(self, key: str, mapping: Mapping[str, float] | dict[str, float], *args: Any, **kwargs: Any) -> "MockPipeline":
        self.commands.append(("zadd", (key, mapping), {}))
        return self

    def zcard(self, key: str) -> "MockPipeline":
        self.commands.append(("zcard", (key,), {}))
        return self

    def expire(self, key: str, seconds: int) -> "MockPipeline":
        self.commands.append(("expire", (key, seconds), {}))
        return self

    async def execute(self) -> list[Any]:
        results = []
        for cmd, args, kwargs in self.commands:
            if cmd == "zremrangebyscore":
                key, min_val, max_val = args
                results.append(self.client._zremrangebyscore(key, min_val, max_val))
            elif cmd == "zadd":
                key, mapping = args
                results.append(self.client._zadd(key, mapping))
            elif cmd == "zcard":
                key, = args
                results.append(self.client._zcard(key))
            elif cmd == "expire":
                key, seconds = args
                results.append(self.client._expire(key, seconds))
        self.commands.clear()
        return results

    async def __aenter__(self) -> "MockPipeline":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class MockRedis:
    """
    An in-memory mock Redis client to serve as a fallback when the real Redis server is unavailable.
    """
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        self.zsets: dict[str, list[tuple[str, float]]] = {}
        self.expirations: dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        if key in self.expirations and time.time() > self.expirations[key]:
            self.data.pop(key, None)
            self.zsets.pop(key, None)
            self.expirations.pop(key, None)
            return True
        return False

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> str | None:
        if self._is_expired(key):
            return None
        val = self.data.get(key)
        return str(val) if val is not None else None

    async def setex(self, key: str, time_secs: int, value: str) -> bool:
        self.data[key] = value
        self.expirations[key] = time.time() + time_secs
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self.data or key in self.zsets:
                self.data.pop(key, None)
                self.zsets.pop(key, None)
                self.expirations.pop(key, None)
                count += 1
        return count

    async def incrby(self, key: str, amount: int = 1) -> int:
        if self._is_expired(key):
            self.data[key] = 0
        val = self.data.get(key, 0)
        try:
            val = int(val)
        except (ValueError, TypeError):
            val = 0
        val += amount
        self.data[key] = val
        return val

    async def close(self) -> None:
        pass

    def pipeline(self, transaction: bool = True) -> MockPipeline:
        return MockPipeline(self)

    # Internal helper methods for Pipeline
    def _zremrangebyscore(self, key: str, min_val: float, max_val: float) -> int:
        self._is_expired(key)
        if key not in self.zsets:
            return 0
        original_len = len(self.zsets[key])
        self.zsets[key] = [
            (member, score) for member, score in self.zsets[key]
            if not (min_val <= score <= max_val)
        ]
        return original_len - len(self.zsets[key])

    def _zadd(self, key: str, mapping: Mapping[str, float] | dict[str, float]) -> int:
        self._is_expired(key)
        if key not in self.zsets:
            self.zsets[key] = []
        added = 0
        for member, score in mapping.items():
            self.zsets[key] = [(m, s) for m, s in self.zsets[key] if m != member]
            self.zsets[key].append((member, score))
            added += 1
        return added

    def _zcard(self, key: str) -> int:
        self._is_expired(key)
        return len(self.zsets.get(key, []))

    def _expire(self, key: str, seconds: int) -> bool:
        if key in self.data or key in self.zsets:
            self.expirations[key] = time.time() + seconds
            return True
        return False


class RedisManager:
    client: "aioredis.Redis | MockRedis | None" = None

    async def connect_to_redis(self) -> None:
        logger.info("Initiating connection to Redis cluster...")
        try:
            self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.client.ping()
            logger.info("Connection established successfully with Redis.")
        except Exception as exc:
            logger.warning(
                f"Failed to connect to Redis at {settings.REDIS_URL}: {exc}. "
                "Falling back to in-memory MockRedis client for development."
            )
            self.client = MockRedis()

    async def close_redis_connection(self) -> None:
        if self.client and not isinstance(self.client, MockRedis):
            logger.info("Terminating connection pool with Redis...")
            await self.client.close()
            logger.info("Redis connection pool terminated.")

redis_manager = RedisManager()

