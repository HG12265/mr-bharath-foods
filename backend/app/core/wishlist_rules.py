from app.core.exceptions import BaseAppException

MAX_WISHLIST_ITEMS = 100

def validate_wishlist_limit(current_item_count: int) -> None:
    """
    Validates that the wishlist limit of 100 items has not been exceeded.
    """
    if current_item_count >= MAX_WISHLIST_ITEMS:
        raise BaseAppException(
            message=f"Wishlist limit reached. You can have a maximum of {MAX_WISHLIST_ITEMS} items in your wishlist.",
            code="WISHLIST_LIMIT_EXCEEDED",
            status_code=400
        )
