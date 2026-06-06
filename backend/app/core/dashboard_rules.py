from app.core.exceptions import PermissionDeniedException
from app.core.roles import UserRole


def validate_dashboard_access(role: UserRole) -> None:
    """
    Validates if the user role is authorized to view any dashboard metrics.
    Only ADMIN and WAREHOUSE roles are permitted.
    """
    if role not in (UserRole.ADMIN, UserRole.WAREHOUSE):
        raise PermissionDeniedException(
            message="Insufficient clearance. Endpoint requires 'warehouse' clearance level.",
            code="INSUFFICIENT_CLEARANCE",
        )
