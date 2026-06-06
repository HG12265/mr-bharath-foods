from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_WISHLISTS
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[Wishlist]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_WISHLISTS, Wishlist)

    async def get_by_customer_id(self, customer_id: str) -> Wishlist | None:
        """
        Retrieves a non-deleted wishlist by customer ID.
        """
        doc = await self.collection.find_one({"customer_id": customer_id, "is_deleted": {"$ne": True}})
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
