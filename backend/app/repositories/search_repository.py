from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_SEARCH_ANALYTICS
from app.models.search_analytic import SearchAnalytic
from app.repositories.base import BaseRepository


class SearchRepository(BaseRepository[SearchAnalytic]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_SEARCH_ANALYTICS, SearchAnalytic)

    async def get_trending_queries(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Aggregates search_analytics collection to identify the top trending search queries.
        """
        pipeline: list[dict[str, Any]] = [
            {"$group": {"_id": "$query", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {"query": "$_id", "count": 1, "_id": 0}}
        ]
        cursor = await self.collection.aggregate(pipeline)
        results = []
        async for doc in cursor:
            results.append(doc)
        return results
