from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_current_user, get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.shipment import (
    ShipmentCreateRequest,
    ShipmentResponse,
    ShipmentStatusUpdateRequest,
)
from app.services.audit_service import AuditService
from app.services.shipment_service import ShipmentService

router = APIRouter()
admin_router = APIRouter()


def get_shipment_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> ShipmentService:
    repo = ShipmentRepository(db)
    order_repo = OrderRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return ShipmentService(repo, order_repo, audit_service)


@router.post("/order/{order_id}", response_model=Envelope[ShipmentResponse])
async def create_shipment(
    order_id: str,
    payload: ShipmentCreateRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: ShipmentService = Depends(get_shipment_service),
) -> Envelope[ShipmentResponse]:
    """
    Creates a new manual shipment for a paid and confirmed order.
    Restricted to WAREHOUSE or ADMIN roles.
    """
    ip = request.client.host if request.client else None
    shipment = await service.create_shipment(
        order_id=order_id,
        carrier_name=payload.carrier_name,
        tracking_number=payload.tracking_number,
        awb_number=payload.awb_number,
        current_user=current_user,
        ip_address=ip,
    )
    res = service.map_to_response(shipment)
    return Envelope(
        success=True,
        message="Shipment created successfully.",
        data=ShipmentResponse(**res),
    )


@router.get("/order/{order_id}", response_model=Envelope[ShipmentResponse])
async def get_shipment_by_order(
    order_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
) -> Envelope[ShipmentResponse]:
    """
    Retrieve shipment by order ID. Customer can view own shipment; staff can view all.
    """
    shipment = await service.get_shipment_by_order_id(order_id, current_user)
    res = service.map_to_response(shipment)
    return Envelope(
        success=True,
        message="Shipment retrieved successfully.",
        data=ShipmentResponse(**res),
    )


@router.get("/{id}", response_model=Envelope[ShipmentResponse])
async def get_shipment_by_id(
    id: str,
    current_user: TokenData = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
) -> Envelope[ShipmentResponse]:
    """
    Retrieve shipment by shipment ID. Customer can view own shipment; staff can view all.
    """
    shipment = await service.get_shipment_by_id(id, current_user)
    res = service.map_to_response(shipment)
    return Envelope(
        success=True,
        message="Shipment retrieved successfully.",
        data=ShipmentResponse(**res),
    )


@admin_router.patch("/{id}/status", response_model=Envelope[ShipmentResponse])
async def update_shipment_status_admin(
    id: str,
    payload: ShipmentStatusUpdateRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: ShipmentService = Depends(get_shipment_service),
) -> Envelope[ShipmentResponse]:
    """
    Updates the shipment status and appends a timeline event.
    Restricted to WAREHOUSE or ADMIN roles.
    """
    ip = request.client.host if request.client else None
    shipment = await service.update_shipment_status(
        shipment_id=id,
        status=payload.status,
        message=payload.message,
        location=payload.location,
        current_user=current_user,
        ip_address=ip,
    )
    res = service.map_to_response(shipment)
    return Envelope(
        success=True,
        message="Shipment status updated successfully.",
        data=ShipmentResponse(**res),
    )


@admin_router.get("/", response_model=Envelope[list[ShipmentResponse]])
async def list_all_shipments_admin(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: ShipmentService = Depends(get_shipment_service),
) -> Envelope[list[ShipmentResponse]]:
    """
    Lists all shipments. Restricted to WAREHOUSE or ADMIN roles.
    """
    shipments = await service.get_all_shipments(skip, limit)
    res = [ShipmentResponse(**service.map_to_response(s)) for s in shipments]
    return Envelope(
        success=True,
        message="Shipments listed successfully.",
        data=res,
    )
