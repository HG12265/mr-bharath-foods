from app.core.exceptions import BaseAppException

MAX_QTY_PER_ITEM = 10
MAX_UNIQUE_ROWS = 50

def validate_item_quantity(quantity: int) -> None:
    """
    Validates that the quantity is within allowed bounds (1 to 10).
    """
    if quantity < 1:
        raise BaseAppException(
            message="Quantity must be at least 1.",
            code="INVALID_QUANTITY",
            status_code=400
        )
    if quantity > MAX_QTY_PER_ITEM:
        raise BaseAppException(
            message=f"Quantity cannot exceed {MAX_QTY_PER_ITEM} per item.",
            code="QUANTITY_LIMIT_EXCEEDED",
            status_code=400
        )

def validate_cart_size(unique_rows_count: int, is_new_item: bool) -> None:
    """
    Validates that the cart does not exceed the maximum number of unique items (50).
    """
    if is_new_item and unique_rows_count >= MAX_UNIQUE_ROWS:
        raise BaseAppException(
            message=f"Cart cannot contain more than {MAX_UNIQUE_ROWS} unique items.",
            code="CART_LIMIT_EXCEEDED",
            status_code=400
        )
