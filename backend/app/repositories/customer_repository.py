
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_CUSTOMERS
from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_CUSTOMERS, Customer)

    async def get_by_email(self, email: str) -> Customer | None:
        doc = await self.collection.find_one({"auth.email": email, "is_deleted": {"$ne": True}})
        if doc:
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_by_phone(self, phone: str) -> Customer | None:
        doc = await self.collection.find_one({"auth.phone": phone, "is_deleted": {"$ne": True}})
        if doc:
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def get_by_email_or_phone(self, email_or_phone: str) -> Customer | None:
        doc = await self.collection.find_one({
            "$or": [
                {"auth.email": email_or_phone},
                {"auth.phone": email_or_phone}
            ],
            "is_deleted": {"$ne": True}
        })
        if doc:
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
