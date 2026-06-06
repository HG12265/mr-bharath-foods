from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class CartItem(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    quantity: int
    unit_price_snapshot: Decimal
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Cart(MongoBaseModel):
    customer_id: str | None = None
    guest_token: str | None = None
    items: list[CartItem] = Field(default_factory=list)
    expires_at: datetime | None = None
    status: str = "active"  # active, converted, abandoned
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
