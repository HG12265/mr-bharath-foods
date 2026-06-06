from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_current_user, get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.notification import NotificationResponse
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

router = APIRouter()
admin_router = APIRouter()


def get_notification_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> NotificationService:
    repo = NotificationRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return NotificationService(repo, audit_service)


@router.get("/me", response_model=Envelope[list[NotificationResponse]])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> Envelope[list[NotificationResponse]]:
    """
    Retrieves in-app notifications targeting the current user or their role target group.
    """
    notifications = await service.list_my_notifications(current_user, skip, limit)
    res = [NotificationResponse(**service.map_to_response(n)) for n in notifications]
    return Envelope(
        success=True,
        message="Notifications retrieved successfully.",
        data=res,
    )


@router.patch("/read-all", response_model=Envelope[dict[str, int]])
async def mark_all_notifications_read(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> Envelope[dict[str, int]]:
    """
    Marks all notifications for the current user and their role target group as read.
    """
    ip = request.client.host if request.client else None
    count = await service.mark_all_read(current_user, ip)
    return Envelope(
        success=True,
        message="All notifications marked as read.",
        data={"modified_count": count},
    )


@router.patch("/{id}/read", response_model=Envelope[NotificationResponse])
async def mark_notification_read(
    id: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> Envelope[NotificationResponse]:
    """
    Marks a single notification as read.
    """
    ip = request.client.host if request.client else None
    notification = await service.mark_read(id, current_user, ip)
    res = service.map_to_response(notification)
    return Envelope(
        success=True,
        message="Notification marked as read.",
        data=NotificationResponse(**res),
    )


@admin_router.get("/", response_model=Envelope[list[NotificationResponse]])
async def list_all_notifications_admin(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: NotificationService = Depends(get_notification_service),
) -> Envelope[list[NotificationResponse]]:
    """
    Lists all notifications in the system. Restricted to WAREHOUSE or ADMIN roles.
    """
    notifications = await service.list_admin_notifications(skip, limit)
    res = [NotificationResponse(**service.map_to_response(n)) for n in notifications]
    return Envelope(
        success=True,
        message="All system notifications retrieved successfully.",
        data=res,
    )
