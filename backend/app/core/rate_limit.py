import time

from fastapi import Request

from app.core.exceptions import RateLimitException
from app.core.redis import redis_manager


async def check_rate_limit(
    request: Request,
    key_prefix: str = "rate_limit",
    limit: int = 100,
    window_seconds: int = 60
) -> None:
    """
    Sliding window rate-limiting check using Redis Sorted Sets (ZSET).
    """
    if not redis_manager.client:
        return  # Fallback: ignore rate limits if Redis is offline

    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}"

    now = time.time()
    cutoff = now - window_seconds

    # Run atomic operations via pipeline
    async with redis_manager.client.pipeline(transaction=True) as pipe:
        # ZREMRANGEBYSCORE: delete log entries older than window cutoff
        pipe.zremrangebyscore(key, 0, cutoff)
        # ZADD: record current timestamps as member and score
        pipe.zadd(key, {str(now): now})
        # ZCARD: retrieve requests count in current log
        pipe.zcard(key)
        # EXPIRE: extend key duration to stay cleaned up
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[2]  # ZCARD result

    if request_count > limit:
        raise RateLimitException(
            message=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds}s allowed."
        )
