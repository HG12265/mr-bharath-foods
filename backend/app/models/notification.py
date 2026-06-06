from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from app.models.base import MongoBaseModel


class Notification(MongoBaseModel):
    target_user_id: str | None = None
    role_target: str | None = None
    type: str
    title: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    read_at: datetime | None = None
    is_deleted: bool = False
