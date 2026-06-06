from decimal import Decimal

FLAT_SHIPPING_FEE = Decimal("50.00")
FREE_SHIPPING_THRESHOLD = Decimal("500.00")


def calculate_shipping_fee(subtotal: Decimal) -> Decimal:
    """
    Computes shipping fee based on subtotal.
    Free shipping for orders equal to or exceeding 500.00.
    """
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0.00")
    return FLAT_SHIPPING_FEE
