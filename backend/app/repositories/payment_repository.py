from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_PAYMENTS
from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_PAYMENTS, Payment)

    async def get_by_order_id(self, order_id: str) -> Payment | None:
        """
        Retrieves a non-deleted payment by its associated order ID.
        """
        doc = await self.collection.find_one(
            {"order_id": order_id, "is_deleted": {"$ne": True}}
        )
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
