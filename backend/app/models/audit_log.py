from datetime import UTC, datetime

from pydantic import Field

from app.models.base import MongoBaseModel


class AuditLog(MongoBaseModel):
    user_id: str | None = None
    action: str
    target_collection: str
    target_id: str | None = None
    ip_address: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
