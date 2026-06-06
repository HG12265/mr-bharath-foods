from datetime import UTC, datetime

from pydantic import Field

from app.models.base import MongoBaseModel


class Category(MongoBaseModel):
    name: str
    slug: str
    description: str | None = None
    image_id: str | None = None
    parent_id: str | None = None
    level: int = 0
    sort_order: int = 0
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
