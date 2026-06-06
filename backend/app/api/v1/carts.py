
from fastapi import APIRouter, Depends, Header, Request, Response
from pymongo.asynchronous.database import AsyncDatabase

from app.core.cart_tokens import generate_guest_token, is_valid_guest_token
from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.core.security import decode_access_token
from app.repositories.audit_repository import AuditRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartMergeRequest,
    CartResponse,
)
from app.schemas.common import Envelope
from app.services.audit_service import AuditService
from app.services.cart_service import CartService

router = APIRouter()


async def get_optional_current_user(
    request: Request,
) -> TokenData | None:
    """
    Optional user dependency. Decodes the Authorization bearer header if present,
    but does not raise exceptions if credentials are missing or invalid.
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split(" ")[1]
    try:
        # Check if access token is blacklisted in Redis if Redis exists
        from app.core.redis import redis_manager

        if redis_manager.client:
            import hashlib

            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            blacklisted = await redis_manager.client.get(f"blacklist:{token_hash}")
            if blacklisted:
                return None

        payload = decode_access_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        role_str = payload.get("role", "customer")

        if not user_id:
            return None

        return TokenData(user_id=user_id, email=email, role=UserRole(role_str))
    except Exception:
        return None


def get_cart_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> CartService:
    repo = CartRepository(db)
    product_repo = ProductRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return CartService(repo, product_repo, audit_service)


@router.get("/me", response_model=Envelope[CartResponse])
async def get_my_cart(
    response: Response,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Retrieves the active cart for the customer or guest user.
    """
    customer_id = None
    guest_token = None

    if current_user:
        customer_id = current_user.user_id
    else:
        if x_guest_token and is_valid_guest_token(x_guest_token):
            guest_token = x_guest_token
        else:
            guest_token = generate_guest_token()

    cart_data = await service.get_cart_with_summaries(
        customer_id=customer_id, guest_token=guest_token
    )

    if guest_token:
        response.headers["X-Guest-Token"] = guest_token

    return Envelope(
        success=True,
        message="Cart retrieved successfully.",
        data=CartResponse(**cart_data),
    )


@router.post("/me/items", response_model=Envelope[CartResponse])
async def add_item_to_cart(
    request: Request,
    response: Response,
    payload: CartItemAdd,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Adds an item (product variant) to the active cart.
    """
    customer_id = None
    guest_token = None
    ip = request.client.host if request.client else None

    if current_user:
        customer_id = current_user.user_id
    else:
        if x_guest_token and is_valid_guest_token(x_guest_token):
            guest_token = x_guest_token
        else:
            guest_token = generate_guest_token()

    await service.add_cart_item(
        customer_id=customer_id,
        guest_token=guest_token,
        product_id=payload.product_id,
        variant_id=payload.variant_id,
        quantity=payload.quantity,
        ip_address=ip,
    )

    cart_data = await service.get_cart_with_summaries(
        customer_id=customer_id, guest_token=guest_token
    )

    if guest_token:
        response.headers["X-Guest-Token"] = guest_token

    return Envelope(
        success=True,
        message="Item added to cart successfully.",
        data=CartResponse(**cart_data),
    )


@router.patch("/me/items/{variant_id}", response_model=Envelope[CartResponse])
async def update_item_quantity_in_cart(
    variant_id: str,
    payload: CartItemUpdate,
    request: Request,
    response: Response,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Updates the quantity of an item in the active cart.
    """
    customer_id = None
    guest_token = None
    ip = request.client.host if request.client else None

    if current_user:
        customer_id = current_user.user_id
    else:
        if x_guest_token and is_valid_guest_token(x_guest_token):
            guest_token = x_guest_token
        else:
            guest_token = generate_guest_token()

    await service.update_cart_item(
        customer_id=customer_id,
        guest_token=guest_token,
        variant_id=variant_id,
        quantity=payload.quantity,
        ip_address=ip,
    )

    cart_data = await service.get_cart_with_summaries(
        customer_id=customer_id, guest_token=guest_token
    )

    if guest_token:
        response.headers["X-Guest-Token"] = guest_token

    return Envelope(
        success=True,
        message="Cart item quantity updated successfully.",
        data=CartResponse(**cart_data),
    )


@router.delete("/me/items/{variant_id}", response_model=Envelope[CartResponse])
async def remove_item_from_cart(
    variant_id: str,
    request: Request,
    response: Response,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Removes an item from the active cart.
    """
    customer_id = None
    guest_token = None
    ip = request.client.host if request.client else None

    if current_user:
        customer_id = current_user.user_id
    else:
        if x_guest_token and is_valid_guest_token(x_guest_token):
            guest_token = x_guest_token
        else:
            guest_token = generate_guest_token()

    await service.remove_cart_item(
        customer_id=customer_id,
        guest_token=guest_token,
        variant_id=variant_id,
        ip_address=ip,
    )

    cart_data = await service.get_cart_with_summaries(
        customer_id=customer_id, guest_token=guest_token
    )

    if guest_token:
        response.headers["X-Guest-Token"] = guest_token

    return Envelope(
        success=True,
        message="Item removed from cart successfully.",
        data=CartResponse(**cart_data),
    )


@router.delete("/me", response_model=Envelope[CartResponse])
async def clear_my_cart(
    request: Request,
    response: Response,
    x_guest_token: str | None = Header(None, alias="X-Guest-Token"),
    current_user: TokenData | None = Depends(get_optional_current_user),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Clears all items in the active cart.
    """
    customer_id = None
    guest_token = None
    ip = request.client.host if request.client else None

    if current_user:
        customer_id = current_user.user_id
    else:
        if x_guest_token and is_valid_guest_token(x_guest_token):
            guest_token = x_guest_token
        else:
            guest_token = generate_guest_token()

    await service.clear_cart(
        customer_id=customer_id, guest_token=guest_token, ip_address=ip
    )

    cart_data = await service.get_cart_with_summaries(
        customer_id=customer_id, guest_token=guest_token
    )

    if guest_token:
        response.headers["X-Guest-Token"] = guest_token

    return Envelope(
        success=True,
        message="Cart cleared successfully.",
        data=CartResponse(**cart_data),
    )


@router.post("/merge", response_model=Envelope[CartResponse])
async def merge_guest_cart_to_customer(
    request: Request,
    payload: CartMergeRequest,
    current_user: TokenData = Depends(require_role(UserRole.CUSTOMER)),
    service: CartService = Depends(get_cart_service),
) -> Envelope[CartResponse]:
    """
    Consolidates the active guest cart into the customer's authenticated cart.
    """
    ip = request.client.host if request.client else None

    await service.merge_carts(
        customer_id=current_user.user_id,
        guest_token=payload.guest_token,
        ip_address=ip,
    )

    cart_data = await service.get_cart_with_summaries(
        customer_id=current_user.user_id
    )

    return Envelope(
        success=True,
        message="Guest cart merged successfully.",
        data=CartResponse(**cart_data),
    )
