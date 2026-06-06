from typing import Any, Generic, TypeVar

from bson import ObjectId
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncDatabase, collection_name: str, model_class: type[T]):  # type: ignore[type-arg]
        self.db = db
        self.collection = db[collection_name]
        self.model_class = model_class

    def _to_object_id(self, id_str: str) -> ObjectId:
        try:
            return ObjectId(id_str)
        except Exception as exc:
            from app.core.exceptions import BaseAppException
            raise BaseAppException(
                message=f"Invalid record identifier format: {id_str}",
                code="INVALID_IDENTIFIER",
                status_code=400
            ) from exc

    async def get_by_id(self, id_str: str) -> T | None:
        obj_id = self._to_object_id(id_str)
        doc = await self.collection.find_one({"_id": obj_id, "is_deleted": {"$ne": True}})
        if doc:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            return self.model_class.model_validate(doc)
        return None

    async def find(self, filter_query: dict[str, Any], skip: int = 0, limit: int = 100) -> list[T]:
        # Enforce soft-delete checks by default across find queries
        full_query = {**filter_query, "is_deleted": {"$ne": True}}
        cursor = self.collection.find(full_query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            results.append(self.model_class.model_validate(doc))
        return results

    async def insert(self, data: BaseModel) -> T:
        doc = data.model_dump(by_alias=True)
        doc["is_deleted"] = False
        from app.core.money import convert_decimals_to_bson
        doc = convert_decimals_to_bson(doc)
        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        doc["_id"] = result.inserted_id
        from app.core.money import convert_bson_to_decimals
        doc = convert_bson_to_decimals(doc)
        return self.model_class.model_validate(doc)

    async def update(self, id_str: str, update_data: dict[str, Any]) -> T | None:
        obj_id = self._to_object_id(id_str)
        # Protect internal keys from update requests
        update_data.pop("_id", None)
        update_data.pop("id", None)
        from app.core.money import convert_decimals_to_bson
        update_data = convert_decimals_to_bson(update_data)

        from pymongo import ReturnDocument
        result = await self.collection.find_one_and_update(
            {"_id": obj_id, "is_deleted": {"$ne": True}},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if result:
            from app.core.money import convert_bson_to_decimals
            result = convert_bson_to_decimals(result)
            result["id"] = str(result["_id"])
            return self.model_class.model_validate(result)
        return None

    async def soft_delete(self, id_str: str) -> bool:
        obj_id = self._to_object_id(id_str)
        result = await self.collection.update_one(
            {"_id": obj_id},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    async def delete(self, id_str: str) -> bool:
        obj_id = self._to_object_id(id_str)
        result = await self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
