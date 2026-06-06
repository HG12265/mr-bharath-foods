from typing import Any

from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_current_user, get_db, require_role
from app.core.roles import UserRole
from app.models.media_asset import MediaAsset
from app.repositories.audit_repository import AuditRepository
from app.repositories.media_repository import MediaRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.media import (
    MediaAssetResponse,
    PresignRequest,
    PresignResponse,
    UploadCompleteRequest,
)
from app.services.audit_service import AuditService
from app.services.media_service import MediaService

router = APIRouter()


def get_media_service(db: Any = Depends(get_db)) -> MediaService:
    repo = MediaRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return MediaService(repo, audit_service)


def map_media_response(asset: MediaAsset) -> MediaAssetResponse:
    return MediaAssetResponse(
        id=asset.id or "",
        original_filename=asset.original_filename,
        content_type=asset.content_type,
        size=asset.size,
        storage_key=asset.storage_key,
        public_url=asset.public_url,
        uploaded_by=asset.uploaded_by,
        asset_type=asset.asset_type,
        status=asset.status,
        created_at=asset.created_at.isoformat()
    )


@router.post("/presign", response_model=Envelope[PresignResponse])
async def request_upload_presign(
    request: Request,
    payload: PresignRequest,
    current_user: TokenData = Depends(get_current_user),
    service: MediaService = Depends(get_media_service)
) -> Envelope[PresignResponse]:
    """
    Validates metadata and generates a secure upload presigned URL.
    """
    ip = request.client.host if request.client else None
    asset, upload_url = await service.generate_presigned_upload(
        user_id=current_user.user_id,
        filename=payload.filename,
        content_type=payload.content_type,
        size=payload.size,
        asset_type=payload.asset_type,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Presigned upload URL generated successfully.",
        data=PresignResponse(
            id=asset.id or "",
            upload_url=upload_url,
            public_url=asset.public_url,
            storage_key=asset.storage_key
        )
    )


@router.post("/complete", response_model=Envelope[MediaAssetResponse])
async def complete_upload_confirmation(
    request: Request,
    payload: UploadCompleteRequest,
    current_user: TokenData = Depends(get_current_user),
    service: MediaService = Depends(get_media_service)
) -> Envelope[MediaAssetResponse]:
    """
    Confirms direct upload completion by performing S3/R2 verification checks.
    """
    ip = request.client.host if request.client else None
    is_admin = current_user.role == UserRole.ADMIN
    asset = await service.confirm_upload_completion(
        user_id=current_user.user_id,
        is_admin=is_admin,
        asset_id=payload.id,
        status=payload.status,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Media upload status confirmed and registered.",
        data=map_media_response(asset)
    )


@router.get("/health", response_model=Envelope[dict[str, str]])
async def check_media_storage_health(
    admin_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: MediaService = Depends(get_media_service)
) -> Envelope[dict[str, str]]:
    """
    Admin health check verifying Cloudflare R2 connectivity.
    """
    healthy = await service.check_storage_health()
    status_str = "healthy" if healthy else "unhealthy"
    return Envelope(
        success=healthy,
        message=f"Media storage connectivity is {status_str}.",
        data={"status": status_str}
    )


@router.get("/{id}", response_model=Envelope[MediaAssetResponse])
async def get_media_asset_metadata(
    id: str,
    current_user: TokenData = Depends(get_current_user),
    service: MediaService = Depends(get_media_service)
) -> Envelope[MediaAssetResponse]:
    """
    Fetches file metadata constraints, enforcing ownership check.
    """
    is_admin = current_user.role == UserRole.ADMIN
    asset = await service.get_media_asset(
        user_id=current_user.user_id,
        is_admin=is_admin,
        asset_id=id
    )
    return Envelope(
        success=True,
        message="Media asset metadata retrieved successfully.",
        data=map_media_response(asset)
    )


@router.delete("/{id}", response_model=Envelope[None])
async def delete_media_asset_record(
    request: Request,
    id: str,
    current_user: TokenData = Depends(get_current_user),
    service: MediaService = Depends(get_media_service)
) -> Envelope[None]:
    """
    Soft-deletes file record metadata, enforcing ownership check.
    """
    ip = request.client.host if request.client else None
    is_admin = current_user.role == UserRole.ADMIN
    await service.soft_delete_media_asset(
        user_id=current_user.user_id,
        is_admin=is_admin,
        asset_id=id,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Media asset soft-deleted successfully."
    )



