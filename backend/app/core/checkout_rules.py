import re

from app.core.exceptions import BaseAppException


def validate_pincode(pincode: str) -> None:
    """
    Validates that the shipping pincode is a standard 6-digit numeric code.
    """
    if not pincode or not re.match(r"^\d{6}$", pincode.strip()):
        raise BaseAppException(
            message="Invalid pincode format. Pincode must be exactly 6 digits.",
            code="INVALID_PINCODE",
            status_code=400,
        )


def validate_phone(phone: str) -> None:
    """
    Validates phone number length and format.
    """
    clean_phone = re.sub(r"\D", "", phone)
    if len(clean_phone) < 10:
        raise BaseAppException(
            message="Invalid phone number. Phone number must contain at least 10 digits.",
            code="INVALID_PHONE",
            status_code=400,
        )


def validate_email(email: str) -> None:
    """
    Validates basic email format structure.
    """
    if not email or "@" not in email:
        raise BaseAppException(
            message="Invalid email address format.",
            code="INVALID_EMAIL",
            status_code=400,
        )
