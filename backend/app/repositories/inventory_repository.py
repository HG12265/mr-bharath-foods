from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_INVENTORIES
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_INVENTORIES, Inventory)

    async def get_by_sku(self, sku: str) -> Inventory | None:
        """
        Retrieves a non-deleted inventory record by variant SKU.
        """
        doc = await self.collection.find_one({"sku": sku, "is_deleted": {"$ne": True}})
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_low_stock_alerts(self) -> list[Inventory]:
        """
        Aggregates inventory entries where available stock (on_hand - reserved)
        is below safety_stock_level.
        """
        from typing import Any
        pipeline: list[dict[str, Any]] = [
            {"$match": {"is_deleted": {"$ne": True}}},
            {
                "$project": {
                    "sku": 1,
                    "variant_id": 1,
                    "product_id": 1,
                    "warehouse_stock": 1,
                    "safety_stock_level": 1,
                    "is_deleted": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "on_hand_total": {
                        "$ifNull": [{"$sum": "$warehouse_stock.on_hand"}, 0]
                    },
                    "reserved_total": {
                        "$ifNull": [{"$sum": "$warehouse_stock.reserved"}, 0]
                    },
                }
            },
            {
                "$project": {
                    "sku": 1,
                    "variant_id": 1,
                    "product_id": 1,
                    "warehouse_stock": 1,
                    "safety_stock_level": 1,
                    "is_deleted": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "available_total": {"$subtract": ["$on_hand_total", "$reserved_total"]},
                }
            },
            {
                "$match": {
                    "$expr": {"$lt": ["$available_total", "$safety_stock_level"]}
                }
            },
        ]

        cursor = await self.collection.aggregate(pipeline)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def create_sku_unique_index(self) -> None:
        """
        Creates a unique index constraint on the sku field.
        """
        await self.collection.create_index("sku", unique=True)
