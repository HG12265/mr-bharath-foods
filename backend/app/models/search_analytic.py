from datetime import UTC, datetime

from pydantic import Field

from app.models.base import MongoBaseModel


class SearchAnalytic(MongoBaseModel):
    query: str
    user_id: str | None = None
    ip_address: str | None = None
    results_count: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
