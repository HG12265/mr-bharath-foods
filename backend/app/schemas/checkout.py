from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ShippingAddressSchema(BaseModel):
    full_name: str = Field(..., description="Recipient's full name")
    phone: str = Field(..., description="Contact phone number")
    address_line1: str = Field(..., description="Primary address details")
    address_line2: str | None = Field(default=None, description="Secondary address layout details")
    city: str = Field(..., description="City placement")
    state: str = Field(..., description="State name")
    pincode: str = Field(..., description="6-digit postal code")
    country: str = Field(default="India", description="Country name")


class CheckoutInitiateRequest(BaseModel):
    cart_id: str = Field(..., description="Target cart identifier")
    email: str = Field(..., description="Customer's billing/notification email")
    shipping_address: ShippingAddressSchema = Field(..., description="Target shipping destination")
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate checkouts")


class CheckoutItemResponse(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    quantity: int
    price: Decimal
    reserved_warehouse_id: str


class CheckoutPricingResponse(BaseModel):
    subtotal: Decimal
    tax_estimate: Decimal
    shipping_fee: Decimal
    coupon_code: str | None = None
    discount: Decimal
    grand_total: Decimal


class CheckoutSessionResponse(BaseModel):
    id: str
    cart_id: str
    customer_id: str | None = None
    guest_token: str | None = None
    email: str
    items: list[CheckoutItemResponse]
    shipping_address: ShippingAddressSchema
    pricing: CheckoutPricingResponse
    status: str
    idempotency_key: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class ApplyCouponRequest(BaseModel):
    coupon_code: str = Field(..., description="Promo code to apply")


class CompleteCheckoutRequest(BaseModel):
    payment_method: str = Field(default="cod", description="Chosen payment method (e.g. cod)")
