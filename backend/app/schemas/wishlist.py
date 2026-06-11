from decimal import Decimal

from pydantic import BaseModel, Field


class WishlistItemAdd(BaseModel):
    product_id: str = Field(..., description="Target product ID")
    variant_id: str = Field(..., description="Target variant ID")

class WishlistProductSummary(BaseModel):
    name: str
    slug: str
    media_ids: list[str] = Field(default_factory=list)
    price: Decimal
    sku: str
    stock_status: str
    volume_weight: str

class WishlistItemResponse(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    added_at: str
    product_summary: WishlistProductSummary

class WishlistResponse(BaseModel):
    id: str
    customer_id: str
    items: list[WishlistItemResponse] = Field(default_factory=list)
    created_at: str
    updated_at: str
