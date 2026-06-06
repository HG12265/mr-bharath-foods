from decimal import Decimal

TAX_RATE = Decimal("0.05")  # Flat 5% GST/tax estimate for foods


def calculate_tax_estimate(subtotal: Decimal) -> Decimal:
    """
    Computes a flat tax estimate using Decimal arithmetic.
    """
    return (subtotal * TAX_RATE).quantize(Decimal("0.01"))
