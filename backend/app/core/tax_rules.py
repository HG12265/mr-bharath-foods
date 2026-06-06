from decimal import Decimal

TAX_RATE = Decimal("0.05")  # Flat 5% GST/tax estimate for foods


def calculate_tax_estimate(subtotal: Decimal, tax_rate: Decimal | None = None) -> Decimal:
    """
    Computes a flat tax estimate using Decimal arithmetic.
    """
    rate = tax_rate if tax_rate is not None else TAX_RATE
    return (subtotal * rate).quantize(Decimal("0.01"))
