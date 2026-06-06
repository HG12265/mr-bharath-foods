from datetime import UTC, datetime

from pydantic import Field

from app.core.review_status import ReviewModerationStatus
from app.models.base import MongoBaseModel


class Review(MongoBaseModel):
    product_id: str
    customer_id: str
    order_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    comment: str
    is_verified_purchase: bool = False
    moderation_status: str = ReviewModerationStatus.PENDING.value
    is_approved: bool = False  # Keep is_approved for quick public filtering
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
