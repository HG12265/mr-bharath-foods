import os
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
    base_url = str(request.base_url)
    asset, upload_url = await service.generate_presigned_upload(
        user_id=current_user.user_id,
        filename=payload.filename,
        content_type=payload.content_type,
        size=payload.size,
        asset_type=payload.asset_type,
        ip_address=ip,
        base_url=base_url
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


@router.put("/upload/mock/{storage_key:path}")
async def upload_mock_file(
    storage_key: str,
    request: Request,
    db: Any = Depends(get_db)
) -> Envelope[dict[str, str]]:
    """
    Local mock endpoint simulating S3 direct file upload PUT requests.
    Uploads directly to Cloudinary or writes locally to static folder depending on config.
    """
    from datetime import UTC, datetime

    from app.core.config import settings
    from app.core.exceptions import BaseAppException
    from app.core.storage import storage_manager

    # 1. Validate request size before processing
    max_size = settings.MAX_REQUEST_SIZE_BYTES
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_size:
                raise BaseAppException(
                    message=f"Upload payload size exceeds limit of {max_size} bytes.",
                    code="PAYLOAD_TOO_LARGE",
                    status_code=413
                )
        except ValueError:
            pass

    try:
        # 2. Read bytes safely using streaming chunks
        body_accumulator = bytearray()
        async for chunk in request.stream():
            body_accumulator.extend(chunk)
            if len(body_accumulator) > max_size:
                raise BaseAppException(
                    message=f"Upload payload size exceeds limit of {max_size} bytes.",
                    code="PAYLOAD_TOO_LARGE",
                    status_code=413
                )
        bytes_data = bytes(body_accumulator)

        if storage_manager.storage_provider == "cloudinary":
            import io
            import re

            import cloudinary
            import cloudinary.uploader

            # Find the corresponding MediaAsset doc by storage_key
            if db is None:
                raise BaseAppException(
                    message="Database connection not initialized.",
                    code="DATABASE_ERROR",
                    status_code=500
                )

            asset = await db["media_assets"].find_one({"storage_key": storage_key, "is_deleted": False})
            if not asset:
                from app.core.exceptions import NotFoundException
                raise NotFoundException("Media asset record not found.")

            asset_type = asset.get("asset_type") or "misc"
            uploaded_by = asset.get("uploaded_by") or "anonymous"

            # Derive public_id without unsafe characters
            filename_with_ext = storage_key.split("/")[-1]
            filename_base, _ = os.path.splitext(filename_with_ext)
            public_id = re.sub(r'[^a-zA-Z0-9._-]', '_', filename_base)

            # Use folder: mr-bharath-foods/{asset_type}/{uploaded_by}
            folder_path = f"mr-bharath-foods/{asset_type}/{uploaded_by}"

            # Initialize Cloudinary credentials securely without exposing in logs
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )

            # TODO: Implement private/signed media URLs for payment proofs in the future
            # to restrict access to sensitive business documents.
            upload_result = cloudinary.uploader.upload(
                io.BytesIO(bytes_data),
                public_id=public_id,
                folder=folder_path,
                overwrite=True,
                resource_type="auto"
            )

            secure_url = upload_result.get("secure_url")
            if not secure_url:
                raise BaseAppException(
                    message="Cloudinary upload failed to return a secure URL.",
                    code="CLOUDINARY_UPLOAD_ERROR",
                    status_code=500
                )

            # Store Cloudinary secure_url into MediaAsset.public_url and mark verifiable
            await db["media_assets"].update_one(
                {"_id": asset["_id"]},
                {"$set": {
                    "public_url": secure_url,
                    "updated_at": datetime.now(UTC)
                }}
            )

            return Envelope(
                success=True,
                message="File uploaded to Cloudinary successfully.",
                data={"storage_key": storage_key, "public_url": secure_url}
            )

        else:
            # Fallback to local file system
            file_path = os.path.join("static", storage_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(bytes_data)

            return Envelope(
                success=True,
                message="Mock file uploaded successfully.",
                data={"storage_key": storage_key}
            )

    except BaseAppException:
        raise
    except Exception as exc:
        raise BaseAppException(
            message=f"Mock file upload failed: {exc!s}",
            code="MOCK_UPLOAD_FAILED",
            status_code=500
        ) from exc


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



