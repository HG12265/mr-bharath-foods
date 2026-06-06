from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class OrderCustomerSnapshot(BaseModel):
    customer_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str | None = None


class OrderAddressSnapshot(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class OrderItem(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    product_name: str
    variant_title: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    reserved_warehouse_id: str


class OrderPricing(BaseModel):
    subtotal: Decimal
    discount: Decimal
    tax_total: Decimal
    shipping_fee: Decimal
    grand_total: Decimal


class Order(MongoBaseModel):
    order_number: str
    checkout_id: str
    customer_id: str | None = None
    guest_token: str | None = None
    customer_snapshot: OrderCustomerSnapshot
    shipping_address_snapshot: OrderAddressSnapshot
    items: list[OrderItem] = Field(default_factory=list)
    pricing: OrderPricing
    payment_status: str = "pending"  # pending | paid | failed | refunded
    fulfillment_status: str = "pending"  # pending | packed | shipped | delivered | cancelled
    order_status: str = "pending_payment"  # pending_payment | confirmed | cancelled | closed
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
