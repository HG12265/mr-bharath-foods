from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MongoBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: str | None = Field(default=None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def convert_object_id(cls, v: Any) -> str | None:
        if isinstance(v, ObjectId):
            return str(v)
        if v is None:
            return None
        return str(v)
