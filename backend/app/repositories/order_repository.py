from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_ORDERS
from app.models.order import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_ORDERS, Order)

    async def get_by_order_number(self, order_number: str) -> Order | None:
        """
        Retrieves an active order by its unique order number.
        """
        doc = await self.collection.find_one(
            {"order_number": order_number, "is_deleted": {"$ne": True}}
        )
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_by_checkout_id(self, checkout_id: str) -> Order | None:
        """
        Retrieves an active order by its checkout session ID.
        """
        doc = await self.collection.find_one(
            {"checkout_id": checkout_id, "is_deleted": {"$ne": True}}
        )
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
