from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_current_user, get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.review import (
    ProductPageResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.audit_service import AuditService
from app.services.review_service import ReviewService

router = APIRouter()
admin_router = APIRouter()


def get_review_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> ReviewService:
    repo = ReviewRepository(db)
    product_repo = ProductRepository(db)
    order_repo = OrderRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)

    from app.repositories.notification_repository import NotificationRepository
    from app.services.notification_service import NotificationService
    noti_repo = NotificationRepository(db)
    notification_service = NotificationService(noti_repo, audit_service)

    return ReviewService(
        repo,
        product_repo,
        order_repo,
        audit_service,
        notification_service,
    )


# --- Customer (and Public) Endpoints ---

@router.post("", response_model=Envelope[ReviewResponse])
async def submit_product_review(
    request: Request,
    payload: ReviewCreate,
    current_user: TokenData = Depends(require_role(UserRole.CUSTOMER)),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[ReviewResponse]:
    """
    Submits a review for moderation. Restricts to customer role.
    """
    ip = request.client.host if request.client else None
    review = await service.submit_review(current_user.user_id, payload, ip)
    return Envelope(
        success=True,
        message="Review submitted successfully for moderation.",
        data=ReviewResponse(**review.model_dump()),
    )


@router.get("/product/{product_id}", response_model=Envelope[ProductPageResponse])
async def get_product_reviews(
    product_id: str,
    service: ReviewService = Depends(get_review_service),
) -> Envelope[ProductPageResponse]:
    """
    Public endpoint retrieving approved product reviews and aggregate stats.
    """
    res = await service.get_product_page_reviews(product_id)
    return Envelope(
        success=True,
        message="Product reviews retrieved successfully.",
        data=res,
    )


@router.patch("/{id}", response_model=Envelope[ReviewResponse])
async def edit_product_review(
    id: str,
    request: Request,
    payload: ReviewUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[ReviewResponse]:
    """
    Updates a customer review (only allowed within 30 days of creation).
    """
    ip = request.client.host if request.client else None
    review = await service.edit_review(current_user.user_id, id, payload, ip)
    return Envelope(
        success=True,
        message="Review updated successfully.",
        data=ReviewResponse(**review.model_dump()),
    )


@router.delete("/{id}", response_model=Envelope[None])
async def delete_product_review(
    id: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[None]:
    """
    Soft-deletes a customer review.
    """
    ip = request.client.host if request.client else None
    # Support deletion by owner customer or admin (using soft delete)
    is_admin = current_user.role == UserRole.ADMIN
    await service.soft_delete_review(current_user.user_id, id, is_admin, ip)
    return Envelope(
        success=True,
        message="Review deleted successfully.",
    )


# --- Admin Moderation Endpoints ---

@admin_router.get("", response_model=Envelope[list[ReviewResponse]])
async def list_all_reviews_admin(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[list[ReviewResponse]]:
    """
    Lists all non-deleted reviews in the system. Requires Admin role.
    """
    reviews = await service.review_repository.list_all_reviews(skip, limit)
    res = [ReviewResponse(**r.model_dump()) for r in reviews]
    return Envelope(
        success=True,
        message="All reviews retrieved successfully for moderation.",
        data=res,
    )


@admin_router.patch("/{id}/approve", response_model=Envelope[ReviewResponse])
async def approve_review_admin(
    id: str,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[ReviewResponse]:
    """
    Approves a review for public viewing. Requires Admin role.
    """
    ip = request.client.host if request.client else None
    review = await service.approve_review(id, current_user.user_id, ip)
    return Envelope(
        success=True,
        message="Review approved successfully.",
        data=ReviewResponse(**review.model_dump()),
    )


@admin_router.patch("/{id}/reject", response_model=Envelope[ReviewResponse])
async def reject_review_admin(
    id: str,
    request: Request,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ReviewService = Depends(get_review_service),
) -> Envelope[ReviewResponse]:
    """
    Rejects/unapproves a review. Requires Admin role.
    """
    ip = request.client.host if request.client else None
    review = await service.reject_review(id, current_user.user_id, ip)
    return Envelope(
        success=True,
        message="Review rejected/unapproved successfully.",
        data=ReviewResponse(**review.model_dump()),
    )
