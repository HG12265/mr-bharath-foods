from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_CATEGORIES
from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_CATEGORIES, Category)

    async def get_by_slug(self, slug: str) -> Category | None:
        """
        Retrieves a non-deleted category by its slug.
        """
        doc = await self.collection.find_one({"slug": slug, "is_deleted": {"$ne": True}})
        if doc:
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_active_categories(self) -> list[Category]:
        """
        Retrieves all active, non-deleted categories.
        """
        cursor = self.collection.find({"is_active": True, "is_deleted": {"$ne": True}})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def get_all_categories(self) -> list[Category]:
        """
        Retrieves all non-deleted categories (including inactive ones).
        """
        cursor = self.collection.find({"is_deleted": {"$ne": True}})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def get_children(self, parent_id: str) -> list[Category]:
        """
        Retrieves all non-deleted direct children of a parent category.
        """
        cursor = self.collection.find({"parent_id": parent_id, "is_deleted": {"$ne": True}})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results
