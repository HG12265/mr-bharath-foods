from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.core.notification_rules import (
    validate_metadata_ids,
    validate_notification_role,
    validate_notification_target,
    validate_notification_type,
)
from app.core.roles import UserRole
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.auth import TokenData
from app.services.audit_service import AuditService
from app.services.base import BaseService


class NotificationService(BaseService[Notification]):
    def __init__(
        self,
        repository: NotificationRepository,
        audit_service: AuditService,
    ):
        super().__init__(repository)
        self.notification_repository = repository
        self.audit_service = audit_service

    async def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        target_user_id: str | None = None,
        role_target: str | None = None,
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
        operator_id: str | None = None,
    ) -> Notification:
        """
        Creates and stores an in-app notification after applying rule checks.
        """
        # 1. Validation
        validate_notification_target(target_user_id, role_target)
        validate_notification_type(type)
        validate_notification_role(role_target)

        meta_payload = metadata or {}
        validate_metadata_ids(meta_payload)

        # 2. Insert notification
        new_notification = Notification(
            target_user_id=target_user_id,
            role_target=role_target,
            type=type,
            title=title,
            message=message,
            metadata=meta_payload,
            is_read=False,
        )

        inserted = await self.notification_repository.insert(new_notification)

        # 3. Log audit
        await self.audit_service.log_action(
            action="CREATE_NOTIFICATION",
            target_collection="notifications",
            user_id=operator_id or "system",
            target_id=inserted.id,
            ip_address=ip_address,
        )

        return inserted

    async def list_my_notifications(
        self,
        current_user: TokenData,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Notification]:
        """
        Retrieves paginated notifications for the current user.
        Customers see only their own. Staff see own plus role-targeted.
        """
        role_filter = None
        if current_user.role in (UserRole.WAREHOUSE, UserRole.ADMIN, UserRole.PARTNER):
            role_filter = current_user.role.value

        return await self.notification_repository.get_for_user_or_role(
            user_id=current_user.user_id,
            role=role_filter,
            skip=skip,
            limit=limit,
        )

    async def mark_read(
        self,
        notification_id: str,
        current_user: TokenData,
        ip_address: str | None = None,
    ) -> Notification:
        """
        Marks a specific notification as read. Validates visibility authorizations.
        """
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification:
            raise NotFoundException(f"Notification '{notification_id}' not found.")

        # Access check
        authorized = False
        if notification.target_user_id == current_user.user_id:
            authorized = True
        elif notification.role_target == current_user.role.value:
            authorized = True

        if not authorized:
            raise PermissionDeniedException("Access forbidden to this notification.")

        # Update
        update_payload = {
            "is_read": True,
            "read_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        updated = await self.notification_repository.update(notification_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to update notification read status.")

        # Log audit
        await self.audit_service.log_action(
            action="READ_NOTIFICATION",
            target_collection="notifications",
            user_id=current_user.user_id,
            target_id=notification_id,
            ip_address=ip_address,
        )

        return updated

    async def mark_all_read(
        self,
        current_user: TokenData,
        ip_address: str | None = None,
    ) -> int:
        """
        Marks all unread notifications for the user or their role target group as read.
        """
        role_filter = None
        if current_user.role in (UserRole.WAREHOUSE, UserRole.ADMIN, UserRole.PARTNER):
            role_filter = current_user.role.value

        count = await self.notification_repository.mark_all_user_or_role_as_read(
            user_id=current_user.user_id,
            role=role_filter,
        )

        # Log audit
        await self.audit_service.log_action(
            action="READ_ALL_NOTIFICATIONS",
            target_collection="notifications",
            user_id=current_user.user_id,
            target_id=None,
            ip_address=ip_address,
        )

        return count

    async def list_admin_notifications(self, skip: int = 0, limit: int = 100) -> list[Notification]:
        """
        Retrieves all notifications in the system (restricted to WAREHOUSE or ADMIN).
        """
        return await self.notification_repository.find({}, skip=skip, limit=limit)

    def map_to_response(self, notification: Notification) -> dict[str, Any]:
        """
        Maps model fields to schema format dictionary.
        """
        return {
            "id": notification.id,
            "target_user_id": notification.target_user_id,
            "role_target": notification.role_target,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "metadata": notification.metadata,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }
