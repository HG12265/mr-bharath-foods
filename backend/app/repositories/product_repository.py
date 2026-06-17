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
        search: str | None = None,
        sort: str | None = None,
        is_featured: bool | None = None,
        skip: int = 0,
        limit: int = 12
    ) -> tuple[list[Product], int]:
        """
        Retrieves active, non-deleted products with filtering, search, sorting and pagination.
        """
        query: dict[str, Any] = {
            "status": "active",
            "is_deleted": {"$ne": True}
        }
        if category_id:
            query["category_id"] = category_id
        if is_featured is not None:
            query["is_featured"] = is_featured

        import re
        if search:
            search = search.strip()[:100]
            escaped_search = re.escape(search)
            search_regex = {"$regex": escaped_search, "$options": "i"}
            query["$or"] = [
                {"name": search_regex},
                {"description": search_regex},
                {"short_description": search_regex},
                {"search_keywords": search_regex}
            ]

        sort_by = []
        if sort in ["price_asc", "price:low-to-high", "price_low_high", "price-low-high"]:
            sort_by.append(("min_price", 1))
        elif sort in ["price_desc", "price:high-to-low", "price_high_low", "price-high-low"]:
            sort_by.append(("min_price", -1))
        elif sort in ["newest", "date_desc", "created_at_desc"]:
            sort_by.append(("created_at", -1))
        elif sort in ["featured", "is_featured"]:
            sort_by.append(("is_featured", -1))
            sort_by.append(("created_at", -1))
        else:
            sort_by.append(("created_at", -1))

        total_count = await self.collection.count_documents(query)

        from app.core.pagination import cap_pagination_limit
        capped_limit = cap_pagination_limit(limit)

        cursor = self.collection.find(query)
        if sort_by:
            cursor = cursor.sort(sort_by)
        cursor = cursor.skip(skip).limit(capped_limit)

        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))

        return results, total_count

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

        from app.core.pagination import cap_pagination_limit
        capped_limit = cap_pagination_limit(limit)
        cursor = self.collection.find(query).skip(skip).limit(capped_limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results
