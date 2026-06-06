from decimal import Decimal

from pydantic import BaseModel, Field


class SourcingDetailsSchema(BaseModel):
    region: str = Field(..., min_length=2, max_length=100)
    story: str = Field(..., min_length=10, max_length=1000)
    manufacturer_id: str | None = Field(None, description="Optional ID referencing manufacturer profile")


class ProductAttributeSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    value: str = Field(..., min_length=1, max_length=100)


class ProductVariantCreate(BaseModel):
    sku: str = Field(..., description="Unique Stock Keeping Unit code")
    title: str = Field(..., min_length=1, max_length=100)
    volume_weight: str = Field(..., description="E.g., 500ml, 1 Liter, 1kg")
    price: Decimal = Field(..., gt=Decimal("0.0"), description="Selling price")
    compare_at_price: Decimal | None = Field(None, gt=Decimal("0.0"), description="Original compare-at price")
    stock_status: str = Field("in_stock", description="in_stock or out_of_stock")
    is_active: bool = Field(True, description="Variant status")


class ProductVariantResponse(BaseModel):
    variant_id: str
    sku: str
    title: str
    volume_weight: str
    price: Decimal
    compare_at_price: Decimal | None
    stock_status: str
    is_active: bool


class SEOMetadataSchema(BaseModel):
    meta_title: str | None = Field(None, max_length=100)
    meta_description: str | None = Field(None, max_length=200)
    meta_keywords: list[str] = Field(default_factory=list)


class ProductRatingsSchema(BaseModel):
    average_rating: float
    review_count: int
    total_reviews: int
    star_1_count: int
    star_2_count: int
    star_3_count: int
    star_4_count: int
    star_5_count: int


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str = Field(..., min_length=10, max_length=2000)
    short_description: str = Field(..., min_length=5, max_length=300)
    category_id: str = Field(..., description="Referenced active category ID")
    media_ids: list[str] = Field(default_factory=list, description="Referenced completed media asset IDs")
    sourcing: SourcingDetailsSchema
    attributes: list[ProductAttributeSchema] = Field(default_factory=list)
    variants: list[ProductVariantCreate] = Field(default_factory=list)
    seo: SEOMetadataSchema | None = Field(None)
    tags: list[str] = Field(default_factory=list)
    search_keywords: list[str] = Field(default_factory=list)
    is_featured: bool = Field(False)
    status: str = Field("draft", description="draft, active, archived")


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None, min_length=10, max_length=2000)
    short_description: str | None = Field(None, min_length=5, max_length=300)
    category_id: str | None = Field(None)
    media_ids: list[str] | None = Field(None)
    sourcing: SourcingDetailsSchema | None = Field(None)
    attributes: list[ProductAttributeSchema] | None = Field(None)
    variants: list[ProductVariantCreate] | None = Field(None)
    seo: SEOMetadataSchema | None = Field(None)
    tags: list[str] | None = Field(None)
    search_keywords: list[str] | None = Field(None)
    is_featured: bool | None = Field(None)
    status: str | None = Field(None)


class ProductStatusUpdate(BaseModel):
    status: str = Field(..., description="draft, active, archived")


class ProductResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    short_description: str
    category_id: str
    media_ids: list[str]
    sourcing: SourcingDetailsSchema
    attributes: list[ProductAttributeSchema]
    variants: list[ProductVariantResponse]
    seo: SEOMetadataSchema
    ratings: ProductRatingsSchema
    tags: list[str]
    search_keywords: list[str]
    is_featured: bool
    status: str
    created_at: str
    updated_at: str
