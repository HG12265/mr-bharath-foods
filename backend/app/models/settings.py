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
    # Business Identity
    brand_name: str | None = None
    support_email: str | None = None
    support_phone: str | None = None
    business_address: str | None = None
    # Payment Settings
    payment_display_name: str | None = None
    upi_instructions: str | None = None
    # Storefront Contact
    public_support_email: str | None = None
    public_support_phone: str | None = None
    working_hours: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
