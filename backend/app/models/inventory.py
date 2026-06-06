from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel


class WarehouseStock(BaseModel):
    warehouse_id: str
    on_hand: int = Field(default=0, ge=0)
    reserved: int = Field(default=0, ge=0)
    location_code: str | None = None


class Inventory(MongoBaseModel):
    sku: str
    variant_id: str
    product_id: str
    warehouse_stock: list[WarehouseStock] = Field(default_factory=list)
    safety_stock_level: int = Field(default=0, ge=0)
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
