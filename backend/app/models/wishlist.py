from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class WishlistItem(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class Wishlist(MongoBaseModel):
    customer_id: str
    items: list[WishlistItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
