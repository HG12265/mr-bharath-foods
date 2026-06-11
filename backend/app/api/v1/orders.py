from typing import Any
from fastapi import APIRouter, Depends, Header, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.api.v1.carts import get_optional_current_user
from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.checkout_repository import CheckoutRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.order import AdminOrderStatusUpdateSchema, OrderResponse
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService

router = APIRouter()
admin_router = APIRouter()


def get_order_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> OrderService:
    repo = OrderRepository(db)
    checkout_repo = CheckoutRepository(db)
    customer_repo = CustomerRepository(db)
    product_repo = ProductRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    inventory_repo = InventoryRepository(db)

    from app.repositories.notification_repository import NotificationRepository
    from app.services.notification_service import NotificationService
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo, audit_service)

    inventory_service = InventoryService(
        inventory_repo, product_repo, audit_service, notification_service
    )
    return OrderService(
        repo,
        checkout_repo,
        customer_repo,
        product_repo,
        inventory_service,
        audit_service,
        notification_service,
    )


@router.post("/from-checkout/{checkout_id}", response_model=Envelope[OrderResponse])
async def create_order_from_checkout(
    checkout_id: str,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: OrderService = Depends(get_order_service),
) -> Envelope[OrderResponse]:
    """
    Converts a completed checkout session into a pending order.
    """
    ip = request.client.host if request.client else None
    order = await service.create_order_from_checkout(
        checkout_id=checkout_id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )
    res = service.map_to_response(order)
    return Envelope(
        success=True,
        message="Order created successfully.",
        data=OrderResponse(**res),
    )


@router.get("/me", response_model=Envelope[list[OrderResponse]])
async def get_my_order_history(
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: OrderService = Depends(get_order_service),
) -> Envelope[list[OrderResponse]]:
    """
    Retrieves order history for the current authenticated user or active guest token.
    """
    orders = await service.get_order_history(
        current_user=current_user, guest_token=x_guest_token
    )
    res_list = [OrderResponse(**service.map_to_response(o)) for o in orders]
    return Envelope(
        success=True,
        message="Order history retrieved successfully.",
        data=res_list,
    )


@router.get("/{id}", response_model=Envelope[OrderResponse])
async def get_order_by_id(
    id: str,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: OrderService = Depends(get_order_service),
) -> Envelope[OrderResponse]:
    """
    Retrieves a single order by its ID. Requires proper ownership or admin clearance.
    """
    ip = request.client.host if request.client else None
    order = await service.get_order_by_id(
        order_id=id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )
    res = service.map_to_response(order)
    return Envelope(
        success=True,
        message="Order retrieved successfully.",
        data=OrderResponse(**res),
    )


@router.post("/{id}/cancel", response_model=Envelope[OrderResponse])
async def cancel_order(
    id: str,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: OrderService = Depends(get_order_service),
) -> Envelope[OrderResponse]:
    """
    Cancels an unpaid pending order. Releases reserved inventory back to warehouse stock.
    """
    ip = request.client.host if request.client else None
    order = await service.cancel_order(
        order_id=id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )
    res = service.map_to_response(order)
    return Envelope(
        success=True,
        message="Order cancelled successfully.",
        data=OrderResponse(**res),
    )


@router.get("/{id}/invoice")
async def get_order_invoice(
    id: str,
    request: Request,
    mode: str = "download",
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
    service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Generates and returns the invoice PDF dynamically from live order data.
    Supports mode=view (inline disposition) and mode=download (attachment disposition).
    Enforces that the customer can only access their own order, while admin/warehouse can access it.
    Only allowed if payment_status is 'paid'.
    """
    from fastapi.responses import StreamingResponse
    from app.core.exceptions import BaseAppException
    from app.services.invoice_service import InvoiceService
    from app.repositories.settings_repository import SettingsRepository
    from app.services.settings_service import SettingsService

    ip = request.client.host if request.client else None

    # Retrieve order - this automatically enforces customer/guest ownership or staff role clearance
    order = await service.get_order_by_id(
        order_id=id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )

    # Restrict invoice availability to paid orders only
    if order.payment_status != "paid":
        raise BaseAppException(
            message="Invoice PDF can only be generated for paid orders.",
            code="ORDER_NOT_PAID",
            status_code=400,
        )

    # Initialize InvoiceService & SettingsService
    invoice_service = InvoiceService(service.order_repository, service.audit_service)
    settings_repo = SettingsRepository(db)
    settings_service = SettingsService(settings_repo, service.audit_service)

    operator_id = current_user.user_id if current_user else "guest"

    # Ensure invoice reference metadata exists in order document
    invoice_number, _ = await invoice_service.ensure_invoice_metadata(
        order, operator_id=operator_id, ip_address=ip
    )

    # Fetch global business details
    settings_doc = await settings_service.get_or_create_default_settings()

    # Generate dynamic ReportLab PDF in memory (BytesIO)
    pdf_buffer = invoice_service.generate_invoice_pdf(order, settings_doc)

    # Log specific audit action
    audit_action = "INVOICE_DOWNLOADED" if mode == "download" else "INVOICE_VIEWED"
    await service.audit_service.log_action(
        action=audit_action,
        target_collection="orders",
        user_id=operator_id,
        target_id=order.id,
        ip_address=ip,
    )

    # Configure content-disposition
    filename = f"invoice-{invoice_number}.pdf"
    disposition = "attachment" if mode == "download" else "inline"
    headers = {
        "Content-Disposition": f'{disposition}; filename="{filename}"',
        "Content-Type": "application/pdf",
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)


# --- ADMIN ROUTER ENDPOINTS ---


@admin_router.get("/", response_model=Envelope[list[OrderResponse]])
async def get_admin_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: OrderService = Depends(get_order_service),
) -> Envelope[list[OrderResponse]]:
    """
    Retrieves all orders. Restrict access to ADMIN or WAREHOUSE roles.
    """
    orders = await service.get_admin_orders(skip=skip, limit=limit)
    res_list = [OrderResponse(**service.map_to_response(o)) for o in orders]
    return Envelope(
        success=True,
        message="All orders retrieved successfully.",
        data=res_list,
    )


@admin_router.patch("/{id}/status", response_model=Envelope[OrderResponse])
async def update_order_status(
    id: str,
    payload: AdminOrderStatusUpdateSchema,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: OrderService = Depends(get_order_service),
) -> Envelope[OrderResponse]:
    """
    Updates status for an order. Restrict access to ADMIN or WAREHOUSE roles.
    """
    ip = request.client.host if request.client else None
    order = await service.update_order_status_admin(
        order_id=id,
        payload=payload,
        operator_id=current_user.user_id,
        ip_address=ip,
    )
    res = service.map_to_response(order)
    return Envelope(
        success=True,
        message="Order status updated successfully.",
        data=OrderResponse(**res),
    )
