from collections.abc import Iterable
from decimal import Decimal
from typing import Any


def calculate_cart_summary(items: Iterable[Any]) -> dict[str, Any]:
    """
    Calculates cart subtotal, unique item count, and total quantity.
    Each item in 'items' must have 'unit_price_snapshot' (Decimal-compatible) and 'quantity' (int).
    """
    subtotal = Decimal("0.00")
    quantity_total = 0
    unique_items = 0

    for item in items:
        # Support dict access and object attribute access for flexibility
        if isinstance(item, dict):
            price = Decimal(str(item.get("unit_price_snapshot", "0.00")))
            qty = int(item.get("quantity", 0))
        else:
            price = Decimal(str(getattr(item, "unit_price_snapshot", Decimal("0.00"))))
            qty = int(getattr(item, "quantity", 0))

        subtotal += price * qty
        quantity_total += qty
        unique_items += 1

    return {
        "subtotal": subtotal,
        "item_count": unique_items,
        "quantity_total": quantity_total
    }
