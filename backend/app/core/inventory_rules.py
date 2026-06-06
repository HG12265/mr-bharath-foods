from app.core.exceptions import BaseAppException


def validate_reservation_limit(qty_to_reserve: int, available: int) -> None:
    """
    Validates that the quantity to reserve does not exceed the available stock.
    """
    if qty_to_reserve <= 0:
        raise BaseAppException(
            message="Reservation quantity must be greater than zero.",
            code="INVALID_RESERVATION_QUANTITY",
            status_code=400,
        )
    if qty_to_reserve > available:
        raise BaseAppException(
            message=f"Cannot reserve {qty_to_reserve} units. Only {available} units are available.",
            code="INSUFFICIENT_STOCK",
            status_code=400,
        )


def validate_release_limit(qty_to_release: int, reserved: int) -> None:
    """
    Validates that the quantity to release does not exceed the reserved stock.
    """
    if qty_to_release <= 0:
        raise BaseAppException(
            message="Release quantity must be greater than zero.",
            code="INVALID_RELEASE_QUANTITY",
            status_code=400,
        )
    if qty_to_release > reserved:
        raise BaseAppException(
            message=f"Cannot release {qty_to_release} units. Only {reserved} units are reserved.",
            code="RELEASE_LIMIT_EXCEEDED",
            status_code=400,
        )


def validate_adjustment_limit(on_hand: int, delta: int) -> None:
    """
    Validates that the delta adjustment does not make the on-hand quantity negative.
    """
    if on_hand + delta < 0:
        raise BaseAppException(
            message=f"Cannot adjust stock by {delta}. Current on-hand is {on_hand}, which would result in a negative stock level.",
            code="NEGATIVE_STOCK_DISALLOWED",
            status_code=400,
        )
