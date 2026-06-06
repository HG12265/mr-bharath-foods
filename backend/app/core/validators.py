import re

from app.core.exceptions import BaseAppException

# Regex patterns checks
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")
PINCODE_REGEX = re.compile(r"^\d{6}$")

def validate_phone_number(phone: str) -> str:
    """
    Validates E.164 phone number pattern coordinates.
    """
    if not PHONE_REGEX.match(phone):
        raise BaseAppException(
            message="Invalid phone number format. Coordinates must comply with E.164 standards.",
            code="INVALID_PHONE_FORMAT",
            status_code=400
        )
    return phone

def validate_pincode(pincode: str) -> str:
    """
    Validates Indian 6-digit postal pincodes format.
    """
    if not PINCODE_REGEX.match(pincode):
        raise BaseAppException(
            message="Invalid pincode format. Value must contain exactly 6 digits.",
            code="INVALID_PINCODE_FORMAT",
            status_code=400
        )
    return pincode
