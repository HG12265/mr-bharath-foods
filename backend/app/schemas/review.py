from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: str = Field(..., description="ID of the product being reviewed")
    order_id: str = Field(..., description="ID of the delivered order containing the product")
    rating: int = Field(..., ge=1, le=5, description="Star rating between 1 and 5")
    title: str = Field(..., min_length=2, max_length=100, description="Short summary/title of the review")
    comment: str = Field(..., min_length=5, max_length=1000, description="Detailed review text")


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Star rating between 1 and 5")
    title: str = Field(..., min_length=2, max_length=100, description="Short summary/title of the review")
    comment: str = Field(..., min_length=5, max_length=1000, description="Detailed review text")


class ReviewResponse(BaseModel):
    id: str
    product_id: str
    customer_id: str
    order_id: str
    rating: int
    title: str
    comment: str
    is_verified_purchase: bool
    moderation_status: str
    is_approved: bool
    created_at: datetime
    updated_at: datetime


class ProductPageProductDetails(BaseModel):
    name: str


class ProductPageRatingsDetails(BaseModel):
    average: float
    total: int


class ProductPageResponse(BaseModel):
    product: ProductPageProductDetails
    ratings: ProductPageRatingsDetails
    reviews: list[ReviewResponse]
