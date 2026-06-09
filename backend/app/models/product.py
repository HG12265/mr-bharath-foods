from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class SourcingDetails(BaseModel):
    region: str
    story: str
    manufacturer_id: str | None = None


class ProductAttribute(BaseModel):
    name: str
    value: str


class ProductVariant(BaseModel):
    variant_id: str
    sku: str
    title: str
    volume_weight: str
    price: Decimal
    stock_status: str = "in_stock"  # in_stock, out_of_stock
    is_active: bool = True


class SEOMetadata(BaseModel):
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] = Field(default_factory=list)


class ProductRatings(BaseModel):
    average_rating: float = 0.0
    review_count: int = 0
    total_reviews: int = 0
    star_1_count: int = 0
    star_2_count: int = 0
    star_3_count: int = 0
    star_4_count: int = 0
    star_5_count: int = 0


class Product(MongoBaseModel):
    name: str
    slug: str
    description: str
    short_description: str
    category_id: str
    media_ids: list[str] = Field(default_factory=list)
    sourcing: SourcingDetails
    attributes: list[ProductAttribute] = Field(default_factory=list)
    variants: list[ProductVariant] = Field(default_factory=list)
    seo: SEOMetadata = Field(default_factory=SEOMetadata)
    ratings: ProductRatings = Field(default_factory=ProductRatings)
    tags: list[str] = Field(default_factory=list)
    search_keywords: list[str] = Field(default_factory=list)
    is_featured: bool = False
    status: str = "draft"  # draft, active, archived
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
