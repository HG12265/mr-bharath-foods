
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger


class RedisManager:
    client: "aioredis.Redis | None" = None

    async def connect_to_redis(self) -> None:
        logger.info("Initiating connection to Redis cluster...")
        self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await self.client.ping()
        logger.info("Connection established successfully with Redis.")

    async def close_redis_connection(self) -> None:
        if self.client:
            logger.info("Terminating connection pool with Redis...")
            await self.client.close()
            logger.info("Redis connection pool terminated.")

redis_manager = RedisManager()
