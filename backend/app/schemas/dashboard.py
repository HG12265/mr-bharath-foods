from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.inventory import InventoryResponse
from app.schemas.order import OrderResponse
from app.schemas.review import ReviewResponse


class DashboardPaymentProof(BaseModel):
    id: str
    order_id: str
    order_number: str
    amount: Decimal
    status: str
    screenshot_media_id: str | None = None
    created_at: datetime


class DashboardResponse(BaseModel):
    total_orders: int | None = Field(default=None, description="Total order count in system")
    total_revenue: Decimal | None = Field(default=None, description="Total accumulated revenue from paid orders")
    pending_payments: int | None = Field(default=None, description="Count of pending payment proof verifications")
    confirmed_orders: int | None = Field(default=None, description="Count of confirmed orders")
    shipped_orders: int | None = Field(default=None, description="Count of shipped orders")
    delivered_orders: int | None = Field(default=None, description="Count of delivered orders")
    low_stock_count: int | None = Field(default=None, description="Count of low stock inventory items")
    pending_review_count: int | None = Field(default=None, description="Count of reviews pending admin moderation")
    total_customers: int | None = Field(default=None, description="Total active customer registrations")
    total_products: int | None = Field(default=None, description="Total active products in catalog")
    recent_orders: list[OrderResponse] | None = Field(default=None, description="List of recent orders")
    low_stock_alerts: list[InventoryResponse] | None = Field(default=None, description="List of low stock inventory items")
    pending_payment_proofs: list[DashboardPaymentProof] | None = Field(default=None, description="List of pending payment proofs")
    pending_reviews: list[ReviewResponse] | None = Field(default=None, description="List of reviews pending moderation")
