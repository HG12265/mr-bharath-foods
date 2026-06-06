from app.core.exceptions import BaseAppException

VALID_WAREHOUSES = {"WH-MAIN", "WH-NORTH", "WH-SOUTH", "WH-DEFAULT"}


def validate_warehouse_id(warehouse_id: str) -> None:
    """
    Validates that the warehouse ID is non-empty and is a valid system warehouse identifier.
    """
    if not warehouse_id or not warehouse_id.strip():
        raise BaseAppException(
            message="Warehouse ID cannot be empty.",
            code="INVALID_WAREHOUSE",
            status_code=400,
        )

    # Convert to uppercase for standard checks
    wh_upper = warehouse_id.strip().upper()
    if wh_upper not in VALID_WAREHOUSES and not wh_upper.startswith("WH-"):
        raise BaseAppException(
            message=f"Warehouse ID '{warehouse_id}' is not a valid recognized warehouse.",
            code="UNKNOWN_WAREHOUSE",
            status_code=400,
        )
