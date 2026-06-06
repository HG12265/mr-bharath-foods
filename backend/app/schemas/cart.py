from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: str = Field(..., description="Target product ID")
    variant_id: str = Field(..., description="Target variant ID")
    quantity: int = Field(default=1, ge=1, description="Quantity to add")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, description="New quantity")


class CartMergeRequest(BaseModel):
    guest_token: str = Field(..., description="Guest token to merge from")


class CartProductSummary(BaseModel):
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="Product slug")
    media_ids: list[str] = Field(default_factory=list, description="Media asset IDs")
    price: Decimal = Field(..., description="Snapshot/current price")
    sku: str = Field(..., description="Variant SKU")
    stock_status: str = Field(..., description="Variant stock status")


class CartItemResponse(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    quantity: int
    unit_price_snapshot: Decimal
    added_at: datetime
    updated_at: datetime
    product_summary: CartProductSummary | None = None


class CartSummary(BaseModel):
    subtotal: Decimal
    item_count: int
    quantity_total: int


class CartResponse(BaseModel):
    id: str
    customer_id: str | None = None
    guest_token: str | None = None
    items: list[CartItemResponse] = Field(default_factory=list)
    summary: CartSummary
    status: str
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
