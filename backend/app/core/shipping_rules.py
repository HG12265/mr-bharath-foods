from decimal import Decimal

FLAT_SHIPPING_FEE = Decimal("0.00")


def calculate_shipping_fee(
    subtotal: Decimal,
    flat_shipping_fee: Decimal | None = None,
    free_shipping_threshold: Decimal | None = None
) -> Decimal:
    """
    Computes flat shipping fee based on store settings.
    If flat_shipping_fee is 0, shipping is free on all orders.
    """
    if subtotal <= Decimal("0.00"):
        return Decimal("0.00")
    fee = flat_shipping_fee if flat_shipping_fee is not None else FLAT_SHIPPING_FEE
    return fee
