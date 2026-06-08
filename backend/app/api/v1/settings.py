from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.settings_repository import SettingsRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.settings import (
    SettingsAdminResponse,
    SettingsPublicResponse,
    SettingsUpdateSchema,
)
from app.services.audit_service import AuditService
from app.services.settings_service import SettingsService

router = APIRouter()
admin_router = APIRouter()


def get_settings_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> SettingsService:
    repo = SettingsRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return SettingsService(repo, audit_service)


# --- Public Endpoint ---


@router.get("/public", response_model=Envelope[SettingsPublicResponse])
async def get_public_settings(
    service: SettingsService = Depends(get_settings_service),
) -> Envelope[SettingsPublicResponse]:
    """
    Exposes public-safe business details: tax rate, shipping parameters, support contact, FSSAI, and GST.
    Open to all users.
    """
    data = await service.get_public_settings()
    return Envelope(
        success=True,
        message="Public business configurations retrieved successfully.",
        data=data,
    )


# --- Admin Endpoints ---


@admin_router.get("", response_model=Envelope[SettingsAdminResponse])
async def get_admin_settings(
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: SettingsService = Depends(get_settings_service),
) -> Envelope[SettingsAdminResponse]:
    """
    Exposes full administrative business configurations including UPI ID.
    Restricted to Admin.
    """
    data = await service.get_admin_settings()
    return Envelope(
        success=True,
        message="System business configurations retrieved successfully for administration.",
        data=data,
    )


@admin_router.patch("", response_model=Envelope[SettingsAdminResponse])
async def update_admin_settings(
    request: Request,
    payload: SettingsUpdateSchema,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: SettingsService = Depends(get_settings_service),
) -> Envelope[SettingsAdminResponse]:
    """
    Modifies global business settings parameters. Triggers audit log logging.
    Restricted to Admin.
    """
    ip = request.client.host if request.client else None
    updated = await service.update_settings(payload, current_user.user_id, ip)

    # Return mapped admin response
    admin_data = SettingsAdminResponse(
        id=updated.id or "",
        upi_id=updated.upi_id,
        tax_percentage=updated.tax_percentage,
        shipping_fee=updated.shipping_fee,
        free_shipping_threshold=updated.free_shipping_threshold,
        support_contact=updated.support_contact,
        fssai_number=updated.fssai_number,
        gst_number=updated.gst_number,
        brand_name=updated.brand_name,
        support_email=updated.support_email,
        support_phone=updated.support_phone,
        business_address=updated.business_address,
        payment_display_name=updated.payment_display_name,
        upi_instructions=updated.upi_instructions,
        public_support_email=updated.public_support_email,
        public_support_phone=updated.public_support_phone,
        working_hours=updated.working_hours,
    )

    return Envelope(
        success=True,
        message="System configurations modified successfully.",
        data=admin_data,
    )
