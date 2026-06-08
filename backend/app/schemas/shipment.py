from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ShipmentStatus = Literal[
    "pending",
    "packed",
    "shipped",
    "reached_hub",
    "out_for_delivery",
    "delivered",
    "failed",
    "returned",
    "cancelled",
]


class TimelineEventResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    location: str | None = None


class ShipmentCreateRequest(BaseModel):
    carrier_name: str = Field(..., min_length=1)
    tracking_number: str = Field(..., min_length=1)
    awb_number: str | None = Field(default=None)
    estimated_delivery_date: datetime | None = Field(default=None)


class ShipmentEditRequest(BaseModel):
    carrier_name: str | None = Field(default=None)
    tracking_number: str | None = Field(default=None)
    awb_number: str | None = Field(default=None)
    estimated_delivery_date: datetime | None = Field(default=None)


class ShipmentStatusUpdateRequest(BaseModel):
    status: ShipmentStatus
    message: str = Field(..., min_length=1)
    location: str | None = None


class ShipmentResponse(BaseModel):
    id: str
    order_id: str
    order_number: str
    customer_id: str | None = None
    carrier_name: str
    tracking_number: str
    awb_number: str | None = None
    status: str
    timeline: list[TimelineEventResponse]
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    estimated_delivery_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
