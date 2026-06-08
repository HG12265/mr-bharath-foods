from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class TimelineEvent(BaseModel):
    status: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    location: str | None = None


class Shipment(MongoBaseModel):
    order_id: str
    order_number: str
    customer_id: str | None = None
    carrier_name: str
    tracking_number: str
    awb_number: str | None = None
    status: str = "pending"  # pending, packed, shipped, out_for_delivery, delivered, failed, returned
    timeline: list[TimelineEvent] = Field(default_factory=list)
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    estimated_delivery_date: datetime | None = None
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
