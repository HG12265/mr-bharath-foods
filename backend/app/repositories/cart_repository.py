from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_CARTS
from app.models.cart import Cart
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_CARTS, Cart)

    async def get_active_by_customer_id(self, customer_id: str) -> Cart | None:
        """
        Retrieves the active, non-deleted cart for a customer.
        """
        doc = await self.collection.find_one({
            "customer_id": customer_id,
            "status": "active",
            "is_deleted": {"$ne": True}
        })
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_active_by_guest_token(self, guest_token: str) -> Cart | None:
        """
        Retrieves the active, non-deleted cart for a guest token.
        """
        doc = await self.collection.find_one({
            "guest_token": guest_token,
            "status": "active",
            "is_deleted": {"$ne": True}
        })
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def create_ttl_index(self) -> None:
        """
        Creates a TTL index on the expires_at field so that guest carts automatically expire.
        """
        await self.collection.create_index("expires_at", expireAfterSeconds=0)
