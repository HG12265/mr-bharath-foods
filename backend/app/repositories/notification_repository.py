from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_NOTIFICATIONS
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_NOTIFICATIONS, Notification)

    async def get_for_user_or_role(
        self, user_id: str, role: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[Notification]:
        """
        Retrieves notifications targeting either the user specifically,
        or targeting the user's role group, sorted by creation date descending.
        """
        query: dict[str, Any] = {
            "is_deleted": {"$ne": True},
            "$or": [
                {"target_user_id": user_id},
            ]
        }
        if role:
            query["$or"].append({"role_target": role})

        from app.core.pagination import cap_pagination_limit
        capped_limit = cap_pagination_limit(limit)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(capped_limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def mark_all_user_or_role_as_read(
        self, user_id: str, role: str | None = None
    ) -> int:
        """
        Marks all unread notifications matching target user or role as read.
        Returns the number of documents modified.
        """
        from datetime import UTC, datetime
        query: dict[str, Any] = {
            "is_read": False,
            "is_deleted": {"$ne": True},
            "$or": [
                {"target_user_id": user_id},
            ]
        }
        if role:
            query["$or"].append({"role_target": role})

        result = await self.collection.update_many(
            query,
            {"$set": {"is_read": True, "read_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}}
        )
        return result.modified_count
