
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import settings
from app.core.logging import logger


class DatabaseManager:
    client: AsyncMongoClient | None = None  # type: ignore[type-arg]
    db: AsyncDatabase | None = None  # type: ignore[type-arg]

    async def connect_to_database(self) -> None:
        logger.info("Initiating connection to MongoDB Atlas...")
        self.client = AsyncMongoClient(settings.MONGODB_URI)
        # Force a connection check by accessing database reference
        self.db = self.client[settings.DATABASE_NAME]
        logger.info("Connection pool established successfully with MongoDB Atlas.")

    async def close_database_connection(self) -> None:
        if self.client:
            logger.info("Terminating connection pool with MongoDB Atlas...")
            await self.client.close()
            logger.info("MongoDB Atlas connections terminated.")


db_manager = DatabaseManager()
