from datetime import UTC, datetime

from pydantic import Field

from app.models.base import MongoBaseModel


class MediaAsset(MongoBaseModel):
    original_filename: str
    content_type: str
    size: int
    storage_key: str
    public_url: str
    uploaded_by: str
    asset_type: str
    status: str = "pending"  # pending, completed, failed
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
