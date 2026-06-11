
from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.wishlist import (
    WishlistItemAdd,
    WishlistItemResponse,
    WishlistProductSummary,
    WishlistResponse,
)
from app.services.audit_service import AuditService
from app.services.wishlist_service import WishlistService

router = APIRouter()


def get_wishlist_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> WishlistService:
    repo = WishlistRepository(db)
    product_repo = ProductRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return WishlistService(repo, product_repo, audit_service)


@router.get("/me", response_model=Envelope[WishlistResponse])
async def get_my_wishlist(
    current_user: TokenData = Depends(require_role(UserRole.CUSTOMER)),
    service: WishlistService = Depends(get_wishlist_service),
) -> Envelope[WishlistResponse]:
    """
    Retrieves the current customer's wishlist with active product summary data.
    Lazily creates wishlist if missing.
    """
    items = await service.list_wishlist_items_with_summaries(current_user.user_id)
    wishlist = await service.get_or_create_wishlist(current_user.user_id)

    formatted_items = []
    for item in items:
        formatted_items.append(
            WishlistItemResponse(
                product_id=item["product_id"],
                variant_id=item["variant_id"],
                sku=item["sku"],
                added_at=item["added_at"],
                product_summary=WishlistProductSummary(
                    name=item["product_summary"]["name"],
                    slug=item["product_summary"]["slug"],
                    media_ids=item["product_summary"]["media_ids"],
                    price=item["product_summary"]["price"],
                    sku=item["product_summary"]["sku"],
                    stock_status=item["product_summary"]["stock_status"],
                    volume_weight=item["product_summary"]["volume_weight"],
                ),
            )
        )

    res = WishlistResponse(
        id=wishlist.id or "",
        customer_id=wishlist.customer_id,
        items=formatted_items,
        created_at=wishlist.created_at.isoformat(),
        updated_at=wishlist.updated_at.isoformat(),
    )
    return Envelope(success=True, message="Wishlist retrieved successfully.", data=res)


@router.post("/me/items", response_model=Envelope[WishlistResponse])
async def add_item_to_wishlist(
    request: Request,
    payload: WishlistItemAdd,
    current_user: TokenData = Depends(require_role(UserRole.CUSTOMER)),
    service: WishlistService = Depends(get_wishlist_service),
) -> Envelope[WishlistResponse]:
    """
    Adds a product variant to the current customer's wishlist.
    Prevents duplicate items, validates product status, and checks 100-item limit.
    """
    ip = request.client.host if request.client else None
    wishlist = await service.add_wishlist_item(
        customer_id=current_user.user_id,
        product_id=payload.product_id,
        variant_id=payload.variant_id,
        ip_address=ip,
    )

    items = await service.list_wishlist_items_with_summaries(current_user.user_id)

    formatted_items = []
    for item in items:
        formatted_items.append(
            WishlistItemResponse(
                product_id=item["product_id"],
                variant_id=item["variant_id"],
                sku=item["sku"],
                added_at=item["added_at"],
                product_summary=WishlistProductSummary(
                    name=item["product_summary"]["name"],
                    slug=item["product_summary"]["slug"],
                    media_ids=item["product_summary"]["media_ids"],
                    price=item["product_summary"]["price"],
                    sku=item["product_summary"]["sku"],
                    stock_status=item["product_summary"]["stock_status"],
                    volume_weight=item["product_summary"]["volume_weight"],
                ),
            )
        )

    res = WishlistResponse(
        id=wishlist.id or "",
        customer_id=wishlist.customer_id,
        items=formatted_items,
        created_at=wishlist.created_at.isoformat(),
        updated_at=wishlist.updated_at.isoformat(),
    )
    return Envelope(
        success=True, message="Product variant added to wishlist successfully.", data=res
    )


@router.delete("/me/items/{variant_id}", response_model=Envelope[WishlistResponse])
async def remove_item_from_wishlist(
    request: Request,
    variant_id: str,
    current_user: TokenData = Depends(require_role(UserRole.CUSTOMER)),
    service: WishlistService = Depends(get_wishlist_service),
) -> Envelope[WishlistResponse]:
    """
    Removes a product variant from the current customer's wishlist.
    """
    ip = request.client.host if request.client else None
    wishlist = await service.remove_wishlist_item(
        customer_id=current_user.user_id, variant_id=variant_id, ip_address=ip
    )

    items = await service.list_wishlist_items_with_summaries(current_user.user_id)

    formatted_items = []
    for item in items:
        formatted_items.append(
            WishlistItemResponse(
                product_id=item["product_id"],
                variant_id=item["variant_id"],
                sku=item["sku"],
                added_at=item["added_at"],
                product_summary=WishlistProductSummary(
                    name=item["product_summary"]["name"],
                    slug=item["product_summary"]["slug"],
                    media_ids=item["product_summary"]["media_ids"],
                    price=item["product_summary"]["price"],
                    sku=item["product_summary"]["sku"],
                    stock_status=item["product_summary"]["stock_status"],
                    volume_weight=item["product_summary"]["volume_weight"],
                ),
            )
        )

    res = WishlistResponse(
        id=wishlist.id or "",
        customer_id=wishlist.customer_id,
        items=formatted_items,
        created_at=wishlist.created_at.isoformat(),
        updated_at=wishlist.updated_at.isoformat(),
    )
    return Envelope(
        success=True, message="Product variant removed from wishlist successfully.", data=res
    )
