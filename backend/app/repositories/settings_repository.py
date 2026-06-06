from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_SETTINGS
from app.models.settings import Settings
from app.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[Settings]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_SETTINGS, Settings)

    async def get_settings(self) -> Settings | None:
        """
        Retrieves the global settings document.
        """
        doc = await self.collection.find_one({"is_deleted": {"$ne": True}})
        if doc:
            from app.core.money import convert_bson_to_decimals

            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None
