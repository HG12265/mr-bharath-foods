from bson import ObjectId

from app.core.exceptions import BaseAppException
from app.core.notification_types import NotificationType
from app.core.roles import UserRole


def validate_notification_target(target_user_id: str | None, role_target: str | None) -> None:
    """
    Ensures that at least one recipient identifier (user ID or user role target) is specified.
    """
    if not target_user_id and not role_target:
        raise BaseAppException(
            message="Either target_user_id or role_target must be provided for a notification.",
            code="NOTIFICATION_TARGET_REQUIRED",
            status_code=400,
        )


def validate_notification_type(notification_type: str) -> None:
    """
    Verifies that the notification type matches one of the allowed categories.
    """
    try:
        NotificationType(notification_type)
    except ValueError as exc:
        raise BaseAppException(
            message=f"Invalid notification type '{notification_type}'.",
            code="INVALID_NOTIFICATION_TYPE",
            status_code=400,
        ) from exc


def validate_notification_role(role_target: str | None) -> None:
    """
    Verifies that the target role maps to a valid UserRole.
    """
    if role_target is not None:
        try:
            UserRole(role_target)
        except ValueError as exc:
            raise BaseAppException(
                message=f"Invalid target role '{role_target}'.",
                code="INVALID_TARGET_ROLE",
                status_code=400,
            ) from exc


def validate_metadata_ids(metadata: dict[str, str | None]) -> None:
    """
    Validates any ID strings stored inside the metadata payload.
    """
    id_keys = {"order_id", "payment_id", "shipment_id", "inventory_id"}
    for key in id_keys:
        val = metadata.get(key)
        if val is not None:
            try:
                # Basic check: verify format matches string representation of ObjectId
                ObjectId(str(val))
            except Exception as exc:
                raise BaseAppException(
                    message=f"Invalid format for '{key}' in metadata: '{val}'. Must be a valid ObjectId format.",
                    code="INVALID_METADATA_ID",
                    status_code=400,
                ) from exc
