from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_PRODUCTS
from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_PRODUCTS, Product)

    async def get_by_slug(self, slug: str) -> Product | None:
        """
        Retrieves a non-deleted product by its slug.
        """
        doc = await self.collection.find_one({"slug": slug, "is_deleted": {"$ne": True}})
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_by_sku(self, sku: str) -> Product | None:
        """
        Retrieves a non-deleted product that contains a variant matching the given SKU.
        """
        doc = await self.collection.find_one({
            "variants.sku": sku.strip().upper(),
            "is_deleted": {"$ne": True}
        })
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_active_products(
        self,
        category_id: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Product]:
        """
        Retrieves active, non-deleted products, optionally filtered by category.
        """
        query: dict[str, Any] = {
            "status": "active",
            "is_deleted": {"$ne": True}
        }
        if category_id:
            query["category_id"] = category_id

        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def get_all_products(
        self,
        category_id: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Product]:
        """
        Retrieves all non-deleted products (including drafts and archived),
        optionally filtered by category.
        """
        query: dict[str, Any] = {
            "is_deleted": {"$ne": True}
        }
        if category_id:
            query["category_id"] = category_id

        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results
