from datetime import UTC, datetime, timedelta

from app.core.exceptions import BaseAppException
from app.models.order import Order
from app.models.review import Review


def validate_review_creation(
    order: Order | None,
    customer_id: str,
    product_id: str,
    existing_review: Review | None
) -> None:
    """
    Enforces review creation constraints:
    - Delivered orders only.
    - Product exists in delivered order items.
    - Only one active review per customer per product.
    """
    # 1. Order exists
    if not order:
        raise BaseAppException(
            message="Order not found.",
            code="ORDER_NOT_FOUND",
            status_code=404
        )

    # 2. Order customer matches
    if order.customer_id != customer_id:
        raise BaseAppException(
            message="You can only review products from your own orders.",
            code="REVIEW_UNAUTHORIZED_CUSTOMER",
            status_code=403
        )

    # 3. Order is delivered
    if order.fulfillment_status != "delivered":
        raise BaseAppException(
            message="You can only review products from delivered orders.",
            code="ORDER_NOT_DELIVERED",
            status_code=400
        )

    # 4. Product belongs to order items
    product_in_order = any(item.product_id == product_id for item in order.items)
    if not product_in_order:
        raise BaseAppException(
            message="Product does not belong to the specified order.",
            code="PRODUCT_NOT_IN_ORDER",
            status_code=400
        )

    # 5. Only one active review per customer per product
    if existing_review:
        raise BaseAppException(
            message="You have already submitted an active review for this product.",
            code="DUPLICATE_REVIEW",
            status_code=400
        )


def validate_review_edit(review: Review) -> None:
    """
    Enforces review edit constraints:
    - Customer can edit review only within 30 days of creation.
    """
    now = datetime.now(UTC)
    created_at = review.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    if now - created_at > timedelta(days=30):
        raise BaseAppException(
            message="Review can only be edited within 30 days of creation.",
            code="REVIEW_EDIT_EXPIRED",
            status_code=400
        )
