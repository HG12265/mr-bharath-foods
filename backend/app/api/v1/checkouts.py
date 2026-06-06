from fastapi import APIRouter, Depends, Header, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.api.v1.carts import get_optional_current_user
from app.core.dependencies import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.checkout_repository import CheckoutRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.checkout import (
    ApplyCouponRequest,
    CheckoutInitiateRequest,
    CheckoutSessionResponse,
    CompleteCheckoutRequest,
)
from app.schemas.common import Envelope
from app.services.audit_service import AuditService
from app.services.checkout_service import CheckoutService
from app.services.inventory_service import InventoryService

router = APIRouter()


def get_checkout_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> CheckoutService:
    repo = CheckoutRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    inventory_repo = InventoryRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    inventory_service = InventoryService(inventory_repo, product_repo, audit_service)
    return CheckoutService(
        repo, cart_repo, product_repo, inventory_repo, inventory_service, audit_service
    )


@router.post("/initiate", response_model=Envelope[CheckoutSessionResponse])
async def initiate_checkout(
    payload: CheckoutInitiateRequest,
    request: Request,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CheckoutService = Depends(get_checkout_service),
) -> Envelope[CheckoutSessionResponse]:
    """
    Initiates a new checkout session. Reserves inventory and calculates pricing totals.
    """
    customer_id = None
    guest_token = None
    ip = request.client.host if request.client else None

    if current_user:
        customer_id = current_user.user_id
    else:
        guest_token = x_guest_token

    session = await service.initiate_checkout(
        cart_id=payload.cart_id,
        email=payload.email,
        shipping_address=payload.shipping_address,
        idempotency_key=payload.idempotency_key,
        customer_id=customer_id,
        guest_token=guest_token,
        ip_address=ip,
    )

    res = service.map_to_response(session)
    return Envelope(
        success=True,
        message="Checkout session initiated successfully.",
        data=CheckoutSessionResponse(**res),
    )


@router.post("/{checkout_id}/apply-coupon", response_model=Envelope[CheckoutSessionResponse])
async def apply_coupon_code(
    checkout_id: str,
    payload: ApplyCouponRequest,
    request: Request,
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CheckoutService = Depends(get_checkout_service),
) -> Envelope[CheckoutSessionResponse]:
    """
    Applies a coupon to an active checkout session.
    """
    operator_id = current_user.user_id if current_user else "guest"
    ip = request.client.host if request.client else None

    session = await service.apply_coupon(
        checkout_id=checkout_id,
        coupon_code=payload.coupon_code,
        operator_id=operator_id,
        ip_address=ip,
    )

    res = service.map_to_response(session)
    return Envelope(
        success=True,
        message="Coupon applied successfully.",
        data=CheckoutSessionResponse(**res),
    )


@router.post("/{checkout_id}/complete", response_model=Envelope[CheckoutSessionResponse])
async def complete_checkout_session(
    checkout_id: str,
    payload: CompleteCheckoutRequest,
    request: Request,
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CheckoutService = Depends(get_checkout_service),
) -> Envelope[CheckoutSessionResponse]:
    """
    Completes the checkout session. Marks it as completed.
    """
    operator_id = current_user.user_id if current_user else "guest"
    ip = request.client.host if request.client else None

    session = await service.complete_checkout(
        checkout_id=checkout_id,
        operator_id=operator_id,
        ip_address=ip,
    )

    res = service.map_to_response(session)
    return Envelope(
        success=True,
        message="Checkout completed successfully.",
        data=CheckoutSessionResponse(**res),
    )
