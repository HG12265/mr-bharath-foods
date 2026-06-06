from fastapi import APIRouter, Depends, Header, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.api.v1.carts import get_optional_current_user
from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.payment import (
    PaymentInitiateResponse,
    PaymentProofSubmitRequest,
    PaymentProofSubmitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from app.services.audit_service import AuditService
from app.services.payment_service import PaymentService

router = APIRouter()
admin_router = APIRouter()


def get_payment_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> PaymentService:
    repo = PaymentRepository(db)
    order_repo = OrderRepository(db)
    media_repo = MediaRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)

    from app.repositories.notification_repository import NotificationRepository
    from app.services.notification_service import NotificationService
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo, audit_service)

    return PaymentService(
        repo,
        order_repo,
        media_repo,
        audit_service,
        notification_service,
    )


@router.post("/order/{order_id}/initiate", response_model=Envelope[PaymentInitiateResponse])
async def initiate_upi_payment(
    order_id: str,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> Envelope[PaymentInitiateResponse]:
    """
    Initiates the manual UPI payment process. Returns deep link details.
    """
    ip = request.client.host if request.client else None
    payment = await service.initiate_upi_payment(
        order_id=order_id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )
    res = service.map_to_response(payment)
    return Envelope(
        success=True,
        message="UPI payment link generated successfully.",
        data=PaymentInitiateResponse(
            payment_id=res["id"],
            order_id=res["order_id"],
            order_number=res["order_number"],
            amount=res["amount"],
            upi_id=res["upi_id"],
            upi_link=res["upi_link"],
            status=res["status"],
        ),
    )


@router.post("/order/{order_id}/submit-proof", response_model=Envelope[PaymentProofSubmitResponse])
async def submit_payment_proof(
    order_id: str,
    payload: PaymentProofSubmitRequest,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> Envelope[PaymentProofSubmitResponse]:
    """
    Submits a completed screenshot media asset as proof of UPI payment.
    """
    ip = request.client.host if request.client else None
    payment = await service.submit_payment_proof(
        order_id=order_id,
        screenshot_media_id=payload.screenshot_media_id,
        current_user=current_user,
        guest_token=x_guest_token,
        ip_address=ip,
    )
    res = service.map_to_response(payment)
    return Envelope(
        success=True,
        message="Payment proof submitted successfully.",
        data=PaymentProofSubmitResponse(
            payment_id=res["id"],
            status=res["status"],
            screenshot_media_id=res["screenshot_media_id"],
        ),
    )


# --- ADMIN ROUTER ENDPOINTS ---


@admin_router.post("/{payment_id}/verify", response_model=Envelope[PaymentVerifyResponse])
async def verify_payment_proof_admin(
    payment_id: str,
    payload: PaymentVerifyRequest,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: PaymentService = Depends(get_payment_service),
) -> Envelope[PaymentVerifyResponse]:
    """
    Approves or rejects the submitted payment proof. Restricted to ADMIN or WAREHOUSE roles.
    """
    ip = request.client.host if request.client else None
    payment = await service.verify_payment_proof_admin(
        payment_id=payment_id,
        action=payload.action,
        rejection_reason=payload.rejection_reason,
        admin_user_id=current_user.user_id,
        ip_address=ip,
    )
    res = service.map_to_response(payment)

    # Fetch updated order status
    order = await service.order_repository.get_by_id(payment.order_id)
    order_status = order.order_status if order else "unknown"
    order_payment_status = order.payment_status if order else "unknown"

    return Envelope(
        success=True,
        message=f"Payment proof verification completed: {payload.action}.",
        data=PaymentVerifyResponse(
            payment_id=res["id"],
            status=res["status"],
            order_status=order_status,
            payment_status=order_payment_status,
        ),
    )
