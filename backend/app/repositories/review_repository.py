from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_REVIEWS
from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_REVIEWS, Review)

    async def get_by_customer_and_product(self, customer_id: str, product_id: str) -> Review | None:
        """
        Retrieves an active (non-deleted) review for a specific product by a customer.
        """
        doc = await self.collection.find_one({
            "customer_id": customer_id,
            "product_id": product_id,
            "is_deleted": {"$ne": True}
        })
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_approved_reviews_for_product(self, product_id: str) -> list[Review]:
        """
        Retrieves all approved, non-deleted reviews for a product sorted by creation date descending.
        """
        cursor = self.collection.find({
            "product_id": product_id,
            "is_approved": True,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def list_all_reviews(self, skip: int = 0, limit: int = 100) -> list[Review]:
        """
        Retrieves all non-deleted reviews sorted by creation date descending for administrative view.
        """
        from app.core.pagination import cap_pagination_limit
        capped_limit = cap_pagination_limit(limit)
        cursor = self.collection.find({
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1).skip(skip).limit(capped_limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results
