from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.core.notification_types import NotificationType
from app.core.rating_calculator import calculate_ratings_summary
from app.core.review_rules import validate_review_creation, validate_review_edit
from app.core.review_status import ReviewModerationStatus
from app.core.roles import UserRole
from app.models.review import Review
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import (
    ProductPageProductDetails,
    ProductPageRatingsDetails,
    ProductPageResponse,
    ReviewCreate,
    ReviewModerationResponse,
    ReviewResponse,
    ReviewsSummaryResponse,
    ReviewUpdate,
)
from app.services.audit_service import AuditService
from app.services.base import BaseService


class ReviewService(BaseService[Review]):
    def __init__(
        self,
        repository: ReviewRepository,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
        audit_service: AuditService,
        notification_service: Any = None,
        customer_repository: Any = None,
    ):
        super().__init__(repository)
        self.review_repository = repository
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.audit_service = audit_service
        self.notification_service = notification_service
        self.customer_repository = customer_repository

    async def submit_review(
        self,
        customer_id: str,
        request: ReviewCreate,
        ip_address: str | None = None,
    ) -> Review:
        """
        Validates the review submission constraints and records a new product review.
        Triggers an admin notification.
        """
        # 1. Validate product exists
        product = await self.product_repository.get_by_id(request.product_id)
        if not product:
            raise NotFoundException(f"Product '{request.product_id}' not found.")

        # 2. Fetch order
        order = await self.order_repository.get_by_id(request.order_id)

        # 3. Retrieve existing review
        existing = await self.review_repository.get_by_customer_and_product(
            customer_id, request.product_id
        )

        # 4. Enforce validations
        validate_review_creation(order, customer_id, request.product_id, existing)

        # 5. Insert review
        new_review = Review(
            product_id=request.product_id,
            customer_id=customer_id,
            order_id=request.order_id,
            rating=request.rating,
            title=request.title,
            comment=request.comment,
            is_verified_purchase=True,
            moderation_status=ReviewModerationStatus.PENDING.value,
            is_approved=False,
        )

        inserted = await self.review_repository.insert(new_review)

        # 6. Audit submit action
        await self.audit_service.log_action(
            action="SUBMIT_REVIEW",
            target_collection="reviews",
            user_id=customer_id,
            target_id=inserted.id,
            ip_address=ip_address,
        )

        # 7. Notify admin
        if self.notification_service:
            try:
                await self.notification_service.create_notification(
                    type=NotificationType.REVIEW_SUBMITTED.value,
                    title="New review submitted",
                    message=f"New review submitted for {product.name}",
                    role_target=UserRole.ADMIN.value,
                    metadata={"order_id": request.order_id},
                    operator_id=customer_id,
                    ip_address=ip_address,
                )
            except Exception:
                # Notifications should not block execution
                pass

        return inserted

    async def edit_review(
        self,
        customer_id: str,
        review_id: str,
        request: ReviewUpdate,
        ip_address: str | None = None,
    ) -> Review:
        """
        Updates review rating, title, and comment if within 30 days.
        """
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review '{review_id}' not found.")

        if review.customer_id != customer_id:
            raise PermissionDeniedException("You are not authorized to edit this review.")

        # Enforce edit rules
        validate_review_edit(review)

        # Update review
        update_payload = {
            "rating": request.rating,
            "title": request.title,
            "comment": request.comment,
            "updated_at": datetime.now(UTC),
        }

        updated = await self.review_repository.update(review_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to update review details.")

        # Recalculate ratings if the review was already approved and is contributing to stats
        if updated.is_approved:
            await self.recalculate_ratings(updated.product_id)

        # Audit edit action
        await self.audit_service.log_action(
            action="EDIT_REVIEW",
            target_collection="reviews",
            user_id=customer_id,
            target_id=review_id,
            ip_address=ip_address,
        )

        return updated

    async def soft_delete_review(
        self,
        customer_id: str,
        review_id: str,
        is_admin: bool = False,
        ip_address: str | None = None,
    ) -> None:
        """
        Soft-deletes a review. Recalculates product rating statistics if previously approved.
        """
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review '{review_id}' not found.")

        if not is_admin and review.customer_id != customer_id:
            raise PermissionDeniedException("You are not authorized to delete this review.")

        # Perform soft delete
        update_payload = {
            "is_deleted": True,
            "deleted_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

        updated = await self.review_repository.update(review_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to delete review.")

        # Recalculate if it was contributing
        if review.is_approved:
            await self.recalculate_ratings(review.product_id)

        # Audit delete action
        await self.audit_service.log_action(
            action="DELETE_REVIEW",
            target_collection="reviews",
            user_id=customer_id,
            target_id=review_id,
            ip_address=ip_address,
        )

    async def approve_review(
        self,
        review_id: str,
        operator_id: str,
        ip_address: str | None = None,
    ) -> Review:
        """
        Approves a review under moderation. Recalculates stats and notifies customer.
        """
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review '{review_id}' not found.")

        if review.moderation_status == ReviewModerationStatus.APPROVED.value:
            return review

        update_payload = {
            "moderation_status": ReviewModerationStatus.APPROVED.value,
            "is_approved": True,
            "updated_at": datetime.now(UTC),
        }

        updated = await self.review_repository.update(review_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to approve review.")

        # Recalculate product ratings
        await self.recalculate_ratings(updated.product_id)

        # Audit approve action
        await self.audit_service.log_action(
            action="APPROVE_REVIEW",
            target_collection="reviews",
            user_id=operator_id,
            target_id=review_id,
            ip_address=ip_address,
        )

        # Notify customer
        if self.notification_service:
            try:
                await self.notification_service.create_notification(
                    type=NotificationType.REVIEW_APPROVED.value,
                    title="Review approved",
                    message="Your review has been approved",
                    target_user_id=review.customer_id,
                    metadata={"order_id": review.order_id},
                    operator_id=operator_id,
                    ip_address=ip_address,
                )
            except Exception:
                pass

        return updated

    async def reject_review(
        self,
        review_id: str,
        operator_id: str,
        ip_address: str | None = None,
    ) -> Review:
        """
        Rejects/unapproves a review under moderation. Recalculates stats if it was approved.
        """
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review '{review_id}' not found.")

        was_approved = review.is_approved

        update_payload = {
            "moderation_status": ReviewModerationStatus.REJECTED.value,
            "is_approved": False,
            "updated_at": datetime.now(UTC),
        }

        updated = await self.review_repository.update(review_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to reject review.")

        # Recalculate product ratings if previously approved
        if was_approved:
            await self.recalculate_ratings(updated.product_id)

        # Audit reject action
        await self.audit_service.log_action(
            action="REJECT_REVIEW",
            target_collection="reviews",
            user_id=operator_id,
            target_id=review_id,
            ip_address=ip_address,
        )

        return updated

    async def get_product_page_reviews(self, product_id: str) -> ProductPageResponse:
        """
        Builds the ProductPageResponse containing basic product info, ratings, and approved reviews.
        """
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException(f"Product '{product_id}' not found.")

        reviews = await self.review_repository.get_approved_reviews_for_product(product_id)

        # Format details
        prod_details = ProductPageProductDetails(name=product.name)
        ratings_details = ProductPageRatingsDetails(
            average=product.ratings.average_rating,
            total=product.ratings.total_reviews,
        )
        review_responses = [
            ReviewResponse(
                id=r.id or "",
                product_id=r.product_id,
                customer_id=r.customer_id,
                order_id=r.order_id,
                rating=r.rating,
                title=r.title,
                comment=r.comment,
                is_verified_purchase=r.is_verified_purchase,
                moderation_status=r.moderation_status,
                is_approved=r.is_approved,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in reviews
        ]

        return ProductPageResponse(
            product=prod_details,
            ratings=ratings_details,
            reviews=review_responses,
        )

    async def recalculate_ratings(self, product_id: str) -> None:
        """
        Aggregates all approved, non-deleted reviews for a product and updates product document fields.
        """
        approved_reviews = await self.review_repository.get_approved_reviews_for_product(product_id)
        summary = calculate_ratings_summary(approved_reviews)

        # Format subdocument payload
        ratings_payload = {
            "average_rating": float(summary["average_rating"]),
            "review_count": int(summary["review_count"]),
            "total_reviews": int(summary["total_reviews"]),
            "star_1_count": int(summary["star_1_count"]),
            "star_2_count": int(summary["star_2_count"]),
            "star_3_count": int(summary["star_3_count"]),
            "star_4_count": int(summary["star_4_count"]),
            "star_5_count": int(summary["star_5_count"]),
        }

        # Update using product repository collection
        obj_id = self.product_repository._to_object_id(product_id)
        await self.product_repository.collection.update_one(
            {"_id": obj_id},
            {"$set": {"ratings": ratings_payload}}
        )

    # ─────────────────────────────────────────────
    # Enterprise Moderation Methods
    # ─────────────────────────────────────────────

    async def reopen_review(
        self,
        review_id: str,
        operator_id: str,
        ip_address: str | None = None,
    ) -> Review:
        """
        Re-opens a rejected review by setting moderation_status back to 'pending'.
        Recalculates product ratings if the review was previously approved.
        """
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review '{review_id}' not found.")

        if review.moderation_status == ReviewModerationStatus.PENDING.value:
            return review  # Already pending, no-op

        was_approved = review.is_approved

        update_payload = {
            "moderation_status": ReviewModerationStatus.PENDING.value,
            "is_approved": False,
            "updated_at": datetime.now(UTC),
        }

        updated = await self.review_repository.update(review_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to reopen review.")

        # Recalculate product ratings if it was previously approved
        if was_approved:
            await self.recalculate_ratings(updated.product_id)

        # Audit reopen action
        await self.audit_service.log_action(
            action="REOPEN_REVIEW",
            target_collection="reviews",
            user_id=operator_id,
            target_id=review_id,
            ip_address=ip_address,
        )

        return updated

    async def list_reviews_moderation(
        self,
        status: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ReviewModerationResponse]:
        """
        Returns all non-deleted reviews enriched with product name and customer details.
        Supports optional status filter (pending/approved/rejected) and text search.
        """
        from app.core.pagination import cap_pagination_limit
        capped_limit = cap_pagination_limit(limit)

        # Build filter
        query: dict[str, Any] = {"is_deleted": {"$ne": True}}
        if status and status in ("pending", "approved", "rejected"):
            query["moderation_status"] = status

        # Fetch all matching reviews
        cursor = self.review_repository.collection.find(query).sort(
            "created_at", -1
        ).skip(skip).limit(capped_limit)

        reviews_raw: list[dict[str, Any]] = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            reviews_raw.append(doc)

        if not reviews_raw:
            return []

        # Batch-collect unique product_ids and customer_ids
        product_ids = list({r["product_id"] for r in reviews_raw})
        customer_ids = list({r["customer_id"] for r in reviews_raw})

        # Batch-fetch products
        product_map: dict[str, str] = {}
        for pid in product_ids:
            try:
                product = await self.product_repository.get_by_id(pid)
                if product:
                    product_map[pid] = product.name
            except Exception:
                pass

        # Batch-fetch customers
        customer_map: dict[str, dict[str, str]] = {}
        if self.customer_repository:
            for cid in customer_ids:
                try:
                    customer = await self.customer_repository.get_by_id(cid)
                    if customer:
                        first = customer.personal_details.first_name if customer.personal_details else ""
                        last = customer.personal_details.last_name if customer.personal_details else ""
                        email = customer.auth.email if customer.auth else ""
                        customer_map[cid] = {
                            "name": f"{first} {last}".strip(),
                            "email": email,
                        }
                except Exception:
                    pass

        # Build enriched responses
        results: list[ReviewModerationResponse] = []
        for r in reviews_raw:
            product_name = product_map.get(r["product_id"], r.get("product_id", ""))
            cust_info = customer_map.get(r["customer_id"], {})
            customer_name = cust_info.get("name", r.get("customer_id", ""))
            customer_email = cust_info.get("email", "")

            # Apply text search filter (post-fetch for flexibility)
            if search:
                q = search.lower()
                searchable = " ".join([
                    product_name.lower(),
                    customer_name.lower(),
                    customer_email.lower(),
                    r.get("title", "").lower(),
                    r.get("comment", "").lower(),
                ])
                if q not in searchable:
                    continue

            results.append(
                ReviewModerationResponse(
                    id=r["id"],
                    product_id=r["product_id"],
                    customer_id=r["customer_id"],
                    order_id=r["order_id"],
                    rating=r["rating"],
                    title=r["title"],
                    comment=r["comment"],
                    is_verified_purchase=r.get("is_verified_purchase", False),
                    moderation_status=r["moderation_status"],
                    is_approved=r.get("is_approved", False),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    product_name=product_name,
                    customer_name=customer_name,
                    customer_email=customer_email,
                )
            )

        return results

    async def get_reviews_summary(self) -> ReviewsSummaryResponse:
        """
        Returns aggregated counts of all non-deleted reviews grouped by moderation_status.
        """
        collection = self.review_repository.collection
        base_filter = {"is_deleted": {"$ne": True}}

        total = await collection.count_documents(base_filter)
        pending = await collection.count_documents({**base_filter, "moderation_status": "pending"})
        approved = await collection.count_documents({**base_filter, "moderation_status": "approved"})
        rejected = await collection.count_documents({**base_filter, "moderation_status": "rejected"})

        return ReviewsSummaryResponse(
            total=total,
            pending=pending,
            approved=approved,
            rejected=rejected,
        )
