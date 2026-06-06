from decimal import Decimal

FLAT_SHIPPING_FEE = Decimal("50.00")
FREE_SHIPPING_THRESHOLD = Decimal("500.00")


def calculate_shipping_fee(
    subtotal: Decimal,
    flat_shipping_fee: Decimal | None = None,
    free_shipping_threshold: Decimal | None = None
) -> Decimal:
    """
    Computes shipping fee based on subtotal.
    Free shipping for orders equal to or exceeding the threshold.
    """
    fee = flat_shipping_fee if flat_shipping_fee is not None else FLAT_SHIPPING_FEE
    threshold = free_shipping_threshold if free_shipping_threshold is not None else FREE_SHIPPING_THRESHOLD
    if subtotal >= threshold:
        return Decimal("0.00")
    return fee
