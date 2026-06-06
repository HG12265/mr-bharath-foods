from datetime import UTC, datetime
from decimal import Decimal

from pydantic import Field

from app.models.base import MongoBaseModel


class Payment(MongoBaseModel):
    order_id: str
    order_number: str
    customer_id: str | None = None
    guest_token: str | None = None
    amount: Decimal
    upi_id: str
    upi_link: str
    status: str = "pending"  # pending, proof_submitted, approved, rejected
    screenshot_media_id: str | None = None
    transaction_note: str
    rejection_reason: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
