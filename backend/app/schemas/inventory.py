from datetime import datetime

from pydantic import BaseModel, Field


class WarehouseStockSchema(BaseModel):
    warehouse_id: str = Field(..., description="Unique warehouse identifier")
    on_hand: int = Field(default=0, ge=0, description="Physical stock quantity")
    reserved: int = Field(default=0, ge=0, description="Reserved stock quantity")
    location_code: str | None = Field(default=None, description="Location layout code")


class InventoryCreate(BaseModel):
    sku: str = Field(..., description="Globally unique variant SKU")
    variant_id: str = Field(..., description="Target variant identifier")
    product_id: str = Field(..., description="Target product identifier")
    warehouse_stock: list[WarehouseStockSchema] = Field(
        default_factory=list, description="Warehouse level stock entries"
    )
    safety_stock_level: int = Field(
        default=0, ge=0, description="Minimum safety stock threshold"
    )


class InventoryResponse(BaseModel):
    id: str
    sku: str
    variant_id: str
    product_id: str
    warehouse_stock: list[WarehouseStockSchema]
    safety_stock_level: int
    on_hand_total: int
    reserved_total: int
    available_total: int
    is_low_stock: bool
    # Centralized status: healthy | low_stock | out_of_stock
    inventory_status: str
    created_at: datetime
    updated_at: datetime


class InventoryDetailsResponse(InventoryResponse):
    """Extended response that joins product and variant metadata."""
    product_name: str = ""
    variant_name: str = ""
    product_image: str | None = None


class InventoryMovementResponse(BaseModel):
    """A single entry in the inventory movement history log."""
    id: str
    timestamp: datetime
    action: str
    movement_type: str
    quantity: int
    before: int
    after: int
    performed_by: str
    reason: str | None = None


class StockAdjustmentRequest(BaseModel):
    warehouse_id: str = Field(..., description="Warehouse identifier")
    quantity: int = Field(..., description="Quantity delta adjustment (positive/negative)")
    location_code: str | None = Field(default=None, description="Updated layout placement code")
    reason: str | None = Field(default=None, description="Reason for this adjustment (e.g. Purchase Received, Damage, Warehouse Correction)")


class StockReservationRequest(BaseModel):
    warehouse_id: str = Field(..., description="Warehouse identifier")
    quantity: int = Field(..., gt=0, description="Quantity to reserve")


class StockReleaseRequest(BaseModel):
    warehouse_id: str = Field(..., description="Warehouse identifier")
    quantity: int = Field(..., gt=0, description="Quantity to release")
