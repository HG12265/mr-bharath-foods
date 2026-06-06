from decimal import Decimal

from decimal import Decimal
from typing import Any

DEFAULT_SETTINGS: dict[str, Any] = {
    "upi_id": "mrbharathfoods@upi",
    "tax_percentage": Decimal("5.00"),  # 5.00%
    "shipping_fee": Decimal("50.00"),
    "free_shipping_threshold": Decimal("500.00"),
    "support_contact": "support@mrbharathfoods.in",
    "fssai_number": "12345678901234",
    "gst_number": "33AABCM1234D1Z5",
}
