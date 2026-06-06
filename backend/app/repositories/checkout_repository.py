from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_CHECKOUTS
from app.models.checkout import CheckoutSession
from app.repositories.base import BaseRepository


class CheckoutRepository(BaseRepository[CheckoutSession]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_CHECKOUTS, CheckoutSession)

    async def get_by_idempotency_key(self, idempotency_key: str) -> CheckoutSession | None:
        """
        Retrieves a non-deleted checkout session by its unique idempotency key.
        """
        doc = await self.collection.find_one(
            {"idempotency_key": idempotency_key, "is_deleted": {"$ne": True}}
        )
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
