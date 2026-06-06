from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    StockAdjustmentRequest,
    StockReleaseRequest,
    StockReservationRequest,
)
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService

router = APIRouter(dependencies=[Depends(require_role(UserRole.WAREHOUSE))])


def get_inventory_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> InventoryService:
    repo = InventoryRepository(db)
    product_repo = ProductRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return InventoryService(repo, product_repo, audit_service)


@router.get("/alerts/low-stock", response_model=Envelope[list[InventoryResponse]])
async def get_low_stock_alerts(
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[list[InventoryResponse]]:
    """
    Retrieves low stock alerts across all warehouses.
    """
    summaries = await service.list_low_stock_alerts_with_summaries()
    res = [InventoryResponse(**item) for item in summaries]
    return Envelope(
        success=True,
        message="Low stock alerts retrieved successfully.",
        data=res,
    )


@router.get("/{sku}", response_model=Envelope[InventoryResponse])
async def get_inventory_by_sku(
    sku: str,
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Retrieves inventory levels and placement layout locations for a specific variant SKU.
    """
    from app.core.exceptions import NotFoundException

    inventory = await service.inventory_repository.get_by_sku(sku)
    if not inventory:
        raise NotFoundException(f"Inventory record for SKU '{sku}' not found.")

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Inventory record retrieved successfully.",
        data=InventoryResponse(**summary),
    )


@router.post("", response_model=Envelope[InventoryResponse])
async def create_new_inventory(
    payload: InventoryCreate,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Establishes a new trackable inventory record for a variant SKU.
    """
    ip = request.client.host if request.client else None
    inventory = await service.create_inventory(payload, ip_address=ip)

    # Force operator_id override in audit log since create_inventory uses default
    await service.audit_service.log_action(
        action="CREATE_INVENTORY",
        target_collection="inventories",
        user_id=current_user.user_id,
        target_id=inventory.id,
        ip_address=ip,
    )

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Inventory record established successfully.",
        data=InventoryResponse(**summary),
    )


@router.patch("/{sku}/adjust", response_model=Envelope[InventoryResponse])
async def adjust_stock_levels(
    sku: str,
    payload: StockAdjustmentRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Adjusts the stock levels for a specific SKU. Supports positive and negative adjustments.
    """
    ip = request.client.host if request.client else None
    inventory = await service.adjust_stock(
        sku=sku,
        warehouse_id=payload.warehouse_id,
        quantity=payload.quantity,
        location_code=payload.location_code,
        ip_address=ip,
        operator_id=current_user.user_id,
    )

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Stock level adjusted successfully.",
        data=InventoryResponse(**summary),
    )


@router.post("/{sku}/reserve", response_model=Envelope[InventoryResponse])
async def reserve_stock_levels(
    sku: str,
    payload: StockReservationRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Reserves available stock in a warehouse for a variant SKU.
    """
    ip = request.client.host if request.client else None
    inventory = await service.reserve_stock(
        sku=sku,
        warehouse_id=payload.warehouse_id,
        quantity=payload.quantity,
        ip_address=ip,
        operator_id=current_user.user_id,
    )

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Stock reserved successfully.",
        data=InventoryResponse(**summary),
    )


@router.post("/{sku}/release", response_model=Envelope[InventoryResponse])
async def release_stock_levels(
    sku: str,
    payload: StockReleaseRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Releases reserved stock in a warehouse for a variant SKU.
    """
    ip = request.client.host if request.client else None
    inventory = await service.release_stock(
        sku=sku,
        warehouse_id=payload.warehouse_id,
        quantity=payload.quantity,
        ip_address=ip,
        operator_id=current_user.user_id,
    )

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Stock released successfully.",
        data=InventoryResponse(**summary),
    )
