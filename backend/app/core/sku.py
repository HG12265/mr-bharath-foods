import re

from app.core.exceptions import BaseAppException

# SKU must be alphanumeric, uppercase, 3-50 characters, and can include hyphens or underscores
SKU_REGEX = re.compile(r"^[A-Z0-9_-]{3,50}$")


def validate_sku(sku: str) -> str:
    """
    Validates that the SKU follows standard formatting constraints.
    Returns the sanitized, uppercase SKU if valid.
    """
    clean_sku = sku.strip().upper()
    if not SKU_REGEX.match(clean_sku):
        raise BaseAppException(
            message=(
                f"Invalid SKU format: '{sku}'. "
                "SKU must contain 3-50 alphanumeric characters, hyphens, or underscores."
            ),
            code="INVALID_SKU_FORMAT",
            status_code=400
        )
    return clean_sku
