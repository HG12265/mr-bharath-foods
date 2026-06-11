from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

PaymentStatus = Literal["pending", "paid", "failed", "refunded"]
FulfillmentStatus = Literal["pending", "packed", "shipped", "delivered", "cancelled"]
OrderStatus = Literal["pending_payment", "confirmed", "cancelled", "closed"]


class OrderCustomerSnapshotResponse(BaseModel):
    customer_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str | None = None


class OrderAddressSnapshotResponse(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    country: str


class OrderItemResponse(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    product_name: str
    variant_title: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    reserved_warehouse_id: str


class OrderPricingResponse(BaseModel):
    subtotal: Decimal
    discount: Decimal
    tax_total: Decimal
    shipping_fee: Decimal
    grand_total: Decimal


class OrderResponse(BaseModel):
    id: str
    order_number: str
    checkout_id: str
    customer_id: str | None = None
    guest_token: str | None = None
    customer_snapshot: OrderCustomerSnapshotResponse
    shipping_address_snapshot: OrderAddressSnapshotResponse
    items: list[OrderItemResponse] = Field(default_factory=list)
    pricing: OrderPricingResponse
    payment_status: PaymentStatus
    fulfillment_status: FulfillmentStatus
    order_status: OrderStatus
    invoice_number: str | None = None
    invoice_generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminOrderStatusUpdateSchema(BaseModel):
    order_status: OrderStatus | None = None
    payment_status: PaymentStatus | None = None
    fulfillment_status: FulfillmentStatus | None = None
