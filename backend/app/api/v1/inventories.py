import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_AUDIT_LOGS, COLLECTION_CUSTOMERS
from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.inventory import (
    InventoryCreate,
    InventoryDetailsResponse,
    InventoryMovementResponse,
    InventoryResponse,
    StockAdjustmentRequest,
    StockReleaseRequest,
    StockReservationRequest,
)
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService

# Base router: WAREHOUSE and above can access all GET endpoints
router = APIRouter(dependencies=[Depends(require_role(UserRole.WAREHOUSE))])


def get_inventory_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> InventoryService:
    repo = InventoryRepository(db)
    product_repo = ProductRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)

    from app.repositories.notification_repository import NotificationRepository
    from app.services.notification_service import NotificationService
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo, audit_service)

    return InventoryService(
        repo,
        product_repo,
        audit_service,
        notification_service,
    )


# ---------------------------------------------------------------------------
# GET /inventories — Full inventory list joined with product/variant metadata
# ---------------------------------------------------------------------------
@router.get("", response_model=Envelope[list[InventoryDetailsResponse]])
async def list_all_inventories(
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[list[InventoryDetailsResponse]]:
    """
    Lists all inventory records enriched with product name, variant name, and first image.
    Accessible by WAREHOUSE and ADMIN.
    """
    inventories = await service.inventory_repository.find({})
    results: list[InventoryDetailsResponse] = []

    for inv in inventories:
        summary = service.get_inventory_summary(inv)
        # Join product metadata
        product = await service.product_repository.get_by_id(inv.product_id)
        product_name = product.name if product else inv.sku
        variant_name = ""
        product_image: str | None = None

        if product:
            for v in product.variants:
                if v.variant_id == inv.variant_id:
                    variant_name = f"{v.title} ({v.volume_weight})"
                    break
            product_image = product.media_ids[0] if product.media_ids else None

        results.append(
            InventoryDetailsResponse(
                **summary,
                product_name=product_name,
                variant_name=variant_name,
                product_image=product_image,
            )
        )

    return Envelope(
        success=True,
        message="Inventory registry retrieved successfully.",
        data=results,
    )


# ---------------------------------------------------------------------------
# GET /inventories/alerts/low-stock
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# GET /inventories/export/csv — ADMIN only streaming CSV
# ---------------------------------------------------------------------------
@router.get(
    "/export/csv",
    dependencies=[Depends(require_role(UserRole.ADMIN))],
    response_class=StreamingResponse,
)
async def export_inventory_csv(
    service: InventoryService = Depends(get_inventory_service),
) -> StreamingResponse:
    """
    Streams live inventory data as a CSV download. ADMIN only.
    Enterprise-safe: uses StreamingResponse so it handles large catalogs without hanging.
    """
    inventories = await service.inventory_repository.find({})

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Product Name",
        "SKU",
        "Variant",
        "On Hand",
        "Reserved",
        "Available",
        "Safety Stock",
        "Status",
    ])

    for inv in inventories:
        summary = service.get_inventory_summary(inv)
        product = await service.product_repository.get_by_id(inv.product_id)
        product_name = product.name if product else inv.sku
        variant_name = ""
        if product:
            for v in product.variants:
                if v.variant_id == inv.variant_id:
                    variant_name = f"{v.title} ({v.volume_weight})"
                    break

        writer.writerow([
            product_name,
            inv.sku,
            variant_name,
            summary["on_hand_total"],
            summary["reserved_total"],
            summary["available_total"],
            summary["safety_stock_level"],
            summary["inventory_status"],
        ])

    output.seek(0)

    def iter_csv() -> Any:
        yield output.getvalue()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_export.csv"},
    )


# ---------------------------------------------------------------------------
# GET /inventories/{sku}/history — Movement history for a SKU
# ---------------------------------------------------------------------------
@router.get("/{sku}/history", response_model=Envelope[list[InventoryMovementResponse]])
async def get_inventory_history(
    sku: str,
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[list[InventoryMovementResponse]]:
    """
    Retrieves the chronological movement history for a specific SKU from audit logs.
    Resolves performer user_id to readable name/email.
    Accessible by WAREHOUSE and ADMIN.
    """
    from app.core.exceptions import NotFoundException

    inventory = await service.inventory_repository.get_by_sku(sku)
    if not inventory:
        raise NotFoundException(f"Inventory record for SKU '{sku}' not found.")

    # Fetch audit logs for this inventory record
    audit_collection = db[COLLECTION_AUDIT_LOGS]
    cursor = audit_collection.find(
        {
            "target_collection": "inventories",
            "target_id": inventory.id,
        }
    ).sort("timestamp", -1).limit(100)

    logs: list[dict[str, Any]] = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        logs.append(doc)

    # Resolve unique user_ids to names
    user_ids = {log.get("user_id") for log in logs if log.get("user_id")}
    user_map: dict[str, str] = {}
    if user_ids:
        customers_collection = db[COLLECTION_CUSTOMERS]
        async for doc in customers_collection.find(
            {"_id": {"$in": [__import__("bson").ObjectId(uid) for uid in user_ids if _is_valid_objectid(uid)]}},
            {"_id": 1, "auth.email": 1, "auth.phone": 1, "personal_details": 1},
        ):
            uid_str = str(doc["_id"])
            first = (doc.get("personal_details") or {}).get("first_name", "")
            last = (doc.get("personal_details") or {}).get("last_name", "")
            email = (doc.get("auth") or {}).get("email", "")
            name = f"{first} {last}".strip() or email or uid_str
            user_map[uid_str] = name

    movements: list[InventoryMovementResponse] = []
    for log in logs:
        meta: dict[str, Any] = log.get("metadata") or {}
        uid = log.get("user_id") or "system"
        performed_by = user_map.get(uid, uid)

        movements.append(
            InventoryMovementResponse(
                id=log["id"],
                timestamp=log.get("timestamp") or log.get("created_at"),
                action=log.get("action", ""),
                movement_type=meta.get("movement_type", log.get("action", "")),
                quantity=meta.get("quantity", 0),
                before=meta.get("before", 0),
                after=meta.get("after", 0),
                performed_by=performed_by,
                reason=meta.get("reason"),
            )
        )

    return Envelope(
        success=True,
        message="Inventory movement history retrieved successfully.",
        data=movements,
    )


# ---------------------------------------------------------------------------
# GET /inventories/{sku}
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# POST /inventories — ADMIN only: create new inventory record
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=Envelope[InventoryResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def create_new_inventory(
    payload: InventoryCreate,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Establishes a new trackable inventory record for a variant SKU. ADMIN only.
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


# ---------------------------------------------------------------------------
# PATCH /inventories/{sku}/adjust — ADMIN only: adjust stock
# ---------------------------------------------------------------------------
@router.patch(
    "/{sku}/adjust",
    response_model=Envelope[InventoryResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def adjust_stock_levels(
    sku: str,
    payload: StockAdjustmentRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: InventoryService = Depends(get_inventory_service),
) -> Envelope[InventoryResponse]:
    """
    Adjusts the stock levels for a specific SKU. ADMIN only.
    Positive quantity = add stock. Negative quantity = remove stock.
    Enterprise protection: cannot remove more than available (on_hand - reserved).
    """
    ip = request.client.host if request.client else None
    inventory = await service.adjust_stock(
        sku=sku,
        warehouse_id=payload.warehouse_id,
        quantity=payload.quantity,
        location_code=payload.location_code,
        ip_address=ip,
        operator_id=current_user.user_id,
        reason=payload.reason,
    )

    summary = service.get_inventory_summary(inventory)
    return Envelope(
        success=True,
        message="Stock level adjusted successfully.",
        data=InventoryResponse(**summary),
    )


# ---------------------------------------------------------------------------
# POST /inventories/{sku}/reserve — WAREHOUSE and above
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# POST /inventories/{sku}/release — WAREHOUSE and above
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _is_valid_objectid(oid: str) -> bool:
    try:
        __import__("bson").ObjectId(oid)
        return True
    except Exception:
        return False
