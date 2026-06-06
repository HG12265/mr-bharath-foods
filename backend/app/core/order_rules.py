from app.core.exceptions import BaseAppException

VALID_ORDER_STATUS_TRANSITIONS = {
    "pending_payment": {"confirmed", "cancelled"},
    "confirmed": {"closed", "cancelled"},
    "cancelled": set(),
    "closed": set(),
}

VALID_PAYMENT_STATUS_TRANSITIONS = {
    "pending": {"paid", "failed"},
    "paid": {"refunded"},
    "failed": {"pending"},
    "refunded": set(),
}

VALID_FULFILLMENT_STATUS_TRANSITIONS = {
    "pending": {"packed", "shipped", "cancelled"},
    "packed": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def validate_order_status_transition(current: str, target: str) -> None:
    """
    Validates if the transition between order statuses is allowed.
    """
    if current == target:
        return
    allowed = VALID_ORDER_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise BaseAppException(
            message=f"Invalid order status transition from '{current}' to '{target}'.",
            code="INVALID_STATUS_TRANSITION",
            status_code=400,
        )


def validate_payment_status_transition(current: str, target: str) -> None:
    """
    Validates if the transition between payment statuses is allowed.
    """
    if current == target:
        return
    allowed = VALID_PAYMENT_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise BaseAppException(
            message=f"Invalid payment status transition from '{current}' to '{target}'.",
            code="INVALID_STATUS_TRANSITION",
            status_code=400,
        )


def validate_fulfillment_status_transition(current: str, target: str) -> None:
    """
    Validates if the transition between fulfillment statuses is allowed.
    """
    if current == target:
        return
    allowed = VALID_FULFILLMENT_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise BaseAppException(
            message=f"Invalid fulfillment status transition from '{current}' to '{target}'.",
            code="INVALID_STATUS_TRANSITION",
            status_code=400,
        )
