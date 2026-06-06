import re
from decimal import Decimal

from typing import Any

from app.core.exceptions import BaseAppException


def validate_settings_update(data: dict[str, Any]) -> None:
    """
    Enforces format and logic validation constraints on business settings updates.
    """
    # 1. UPI ID format check
    upi_id = data.get("upi_id")
    if upi_id is not None:
        if "@" not in upi_id:
            raise BaseAppException(
                message="Invalid UPI ID format. Must contain '@'.",
                code="INVALID_UPI_ID",
                status_code=400,
            )

    # 2. Tax percentage limit
    tax_percentage = data.get("tax_percentage")
    if tax_percentage is not None:
        if not isinstance(tax_percentage, Decimal):
            tax_percentage = Decimal(str(tax_percentage))
        if tax_percentage < Decimal("0.00") or tax_percentage > Decimal("100.00"):
            raise BaseAppException(
                message="Tax percentage must be between 0.00 and 100.00.",
                code="INVALID_TAX_PERCENTAGE",
                status_code=400,
            )

    # 3. Shipping fee
    shipping_fee = data.get("shipping_fee")
    if shipping_fee is not None:
        if not isinstance(shipping_fee, Decimal):
            shipping_fee = Decimal(str(shipping_fee))
        if shipping_fee < Decimal("0.00"):
            raise BaseAppException(
                message="Shipping fee cannot be negative.",
                code="INVALID_SHIPPING_FEE",
                status_code=400,
            )

    # 4. Free shipping threshold
    free_shipping_threshold = data.get("free_shipping_threshold")
    if free_shipping_threshold is not None:
        if not isinstance(free_shipping_threshold, Decimal):
            free_shipping_threshold = Decimal(str(free_shipping_threshold))
        if free_shipping_threshold < Decimal("0.00"):
            raise BaseAppException(
                message="Free shipping threshold cannot be negative.",
                code="INVALID_FREE_SHIPPING_THRESHOLD",
                status_code=400,
            )

    # 5. FSSAI check
    fssai = data.get("fssai_number")
    if fssai:
        if not re.match(r"^\d{14}$", fssai):
            raise BaseAppException(
                message="Invalid FSSAI number. Must be exactly 14 digits.",
                code="INVALID_FSSAI_NUMBER",
                status_code=400,
            )

    # 6. GST check
    gst = data.get("gst_number")
    if gst:
        if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", gst.upper()):
            raise BaseAppException(
                message="Invalid GST number format.",
                code="INVALID_GST_NUMBER",
                status_code=400,
            )
