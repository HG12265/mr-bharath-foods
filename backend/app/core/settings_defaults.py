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
    "brand_name": "Mr. Bharath Foods",
    "support_email": "support@mrbharathfoods.in",
    "support_phone": "+91 98765 43210",
    "business_address": "",
    "payment_display_name": "Mr. Bharath Foods",
    "upi_instructions": "",
    "public_support_email": "support@mrbharathfoods.in",
    "public_support_phone": "+91 98765 43210",
    "working_hours": "Mon–Sat, 9 AM – 6 PM",
}

