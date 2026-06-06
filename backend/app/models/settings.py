from datetime import UTC, datetime
from decimal import Decimal

from pydantic import Field

from app.models.base import MongoBaseModel


class Settings(MongoBaseModel):
    upi_id: str
    tax_percentage: Decimal
    shipping_fee: Decimal
    free_shipping_threshold: Decimal
    support_contact: str
    fssai_number: str | None = None
    gst_number: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
