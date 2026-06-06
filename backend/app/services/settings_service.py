from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import BaseAppException
from app.core.settings_defaults import DEFAULT_SETTINGS
from app.core.settings_rules import validate_settings_update
from app.models.settings import Settings
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import (
    SettingsAdminResponse,
    SettingsPublicResponse,
    SettingsUpdateSchema,
)
from app.services.audit_service import AuditService
from app.services.base import BaseService


class SettingsService(BaseService[Settings]):
    def __init__(self, repository: SettingsRepository, audit_service: AuditService):
        super().__init__(repository)
        self.settings_repository = repository
        self.audit_service = audit_service

    async def get_or_create_default_settings(self) -> Settings:
        """
        Retrieves the global settings document. If none exists, initializes it
        with DEFAULT_SETTINGS.
        """
        settings = await self.settings_repository.get_settings()
        if settings:
            return settings

        # Create default settings record
        default_model = Settings.model_validate(DEFAULT_SETTINGS)
        inserted = await self.settings_repository.insert(default_model)
        return inserted

    async def get_public_settings(self) -> SettingsPublicResponse:
        """
        Retrieves settings and filters them to contain only public-safe fields.
        """
        settings = await self.get_or_create_default_settings()
        return SettingsPublicResponse(
            tax_percentage=settings.tax_percentage,
            shipping_fee=settings.shipping_fee,
            free_shipping_threshold=settings.free_shipping_threshold,
            support_contact=settings.support_contact,
            fssai_number=settings.fssai_number,
            gst_number=settings.gst_number,
        )

    async def get_admin_settings(self) -> SettingsAdminResponse:
        """
        Retrieves settings for admin operations.
        """
        settings = await self.get_or_create_default_settings()
        return SettingsAdminResponse(
            id=settings.id or "",
            upi_id=settings.upi_id,
            tax_percentage=settings.tax_percentage,
            shipping_fee=settings.shipping_fee,
            free_shipping_threshold=settings.free_shipping_threshold,
            support_contact=settings.support_contact,
            fssai_number=settings.fssai_number,
            gst_number=settings.gst_number,
        )

    async def update_settings(
        self,
        payload: SettingsUpdateSchema,
        operator_id: str,
        ip_address: str | None = None,
    ) -> Settings:
        """
        Validates and updates business settings. Triggers an audit log.
        """
        current = await self.get_or_create_default_settings()

        # Build update payload
        update_data: dict[str, Any] = {}
        dumped = payload.model_dump(exclude_unset=True)

        for k, v in dumped.items():
            if v is not None:
                update_data[k] = v

        if not update_data:
            return current

        # Validate business rules
        validate_settings_update(update_data)

        # Update datetime
        update_data["updated_at"] = datetime.now(UTC)

        updated = await self.settings_repository.update(current.id or "", update_data)
        if not updated:
            raise BaseAppException("Failed to update system settings.")

        # Log audit action
        await self.audit_service.log_action(
            action="UPDATE_SETTINGS",
            target_collection="settings",
            user_id=operator_id,
            target_id=updated.id,
            ip_address=ip_address,
        )

        return updated
