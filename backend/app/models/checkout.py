from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class CheckoutItem(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    quantity: int
    price: Decimal
    reserved_warehouse_id: str


class CheckoutAddress(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class CheckoutSession(MongoBaseModel):
    cart_id: str
    customer_id: str | None = None
    guest_token: str | None = None
    email: str
    items: list[CheckoutItem] = Field(default_factory=list)
    shipping_address: CheckoutAddress
    subtotal: Decimal
    tax_estimate: Decimal
    shipping_fee: Decimal
    coupon_code: str | None = None
    discount: Decimal = Decimal("0.00")
    grand_total: Decimal
    status: str = "initiated"  # initiated, completed, failed, expired
    idempotency_key: str
    is_deleted: bool = False
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
