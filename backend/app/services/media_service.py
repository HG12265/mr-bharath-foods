import os
import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.core.media_rules import validate_media_file
from app.core.storage import storage_manager
from app.models.media_asset import MediaAsset
from app.repositories.media_repository import MediaRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService


class MediaService(BaseService[MediaAsset]):
    def __init__(self, repository: MediaRepository, audit_service: AuditService):
        super().__init__(repository)
        self.media_repository = repository
        self.audit_service = audit_service

    async def generate_presigned_upload(
        self,
        user_id: str,
        filename: str,
        content_type: str,
        size: int,
        asset_type: str,
        ip_address: str | None = None
    ) -> tuple[MediaAsset, str]:
        """
        Validates file metadata, registers a pending asset record in DB,
        and generates a short-lived presigned PUT URL for direct storage upload.
        """
        # Validate file size, mime, and extension constraints
        validate_media_file(filename, content_type, size, asset_type)

        unique_id = str(uuid.uuid4())
        _, ext = os.path.splitext(filename.lower())

        # Sanitize filename to prevent directory traversal or malicious keys
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        if not safe_filename:
            safe_filename = f"file{ext}"

        storage_key = f"media/{asset_type}/{user_id}/{unique_id}-{safe_filename}"

        # Construct public URL based on endpoint and bucket name
        base_endpoint = settings.R2_ENDPOINT_URL or ""
        endpoint_clean = base_endpoint.rstrip("/")
        public_url = f"{endpoint_clean}/{settings.R2_BUCKET_NAME}/{storage_key}"

        # Generate the presigned URL via the storage manager
        upload_url = storage_manager.generate_presigned_put_url(
            key=storage_key,
            content_type=content_type,
            expires_in=3600  # 1 hour expiration
        )

        media_asset = MediaAsset(
            original_filename=filename,
            content_type=content_type,
            size=size,
            storage_key=storage_key,
            public_url=public_url,
            uploaded_by=user_id,
            asset_type=asset_type,
            status="pending"
        )

        inserted_asset = await self.media_repository.insert(media_asset)

        await self.audit_service.log_action(
            action="REQUEST_MEDIA_UPLOAD",
            target_collection="media_assets",
            user_id=user_id,
            target_id=inserted_asset.id,
            ip_address=ip_address
        )

        return inserted_asset, upload_url

    async def confirm_upload_completion(
        self,
        user_id: str,
        is_admin: bool,
        asset_id: str,
        status: str,
        ip_address: str | None = None
    ) -> MediaAsset:
        """
        Verifies if file has been successfully uploaded to R2 and updates DB status accordingly.
        """
        asset = await self.media_repository.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise NotFoundException("Media asset record not found.")

        # Ownership authorization check
        if asset.uploaded_by != user_id and not is_admin:
            raise PermissionDeniedException("You do not have permission to modify this media asset.")

        if status not in ["completed", "failed"]:
            raise BaseAppException(
                message="Invalid upload completion status. Must be 'completed' or 'failed'.",
                code="INVALID_STATUS",
                status_code=400
            )

        update_data: dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(UTC)
        }

        if status == "completed":
            # Verify file exists in R2 storage bucket
            exists = storage_manager.verify_object_exists(asset.storage_key)
            if not exists:
                raise BaseAppException(
                    message="File could not be found in storage. Complete upload before confirmation.",
                    code="FILE_NOT_FOUND_IN_STORAGE",
                    status_code=400
                )

        updated_asset = await self.media_repository.update(asset_id, update_data)
        if not updated_asset:
            raise BaseAppException("Failed to confirm media upload status update.")

        await self.audit_service.log_action(
            action=f"CONFIRM_MEDIA_UPLOAD_{status.upper()}",
            target_collection="media_assets",
            user_id=user_id,
            target_id=asset_id,
            ip_address=ip_address
        )

        return updated_asset

    async def get_media_asset(self, user_id: str, is_admin: bool, asset_id: str) -> MediaAsset:
        """
        Retrieves media asset details, enforcing owner/admin access.
        """
        asset = await self.media_repository.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise NotFoundException("Media asset record not found.")

        if asset.uploaded_by != user_id and not is_admin:
            raise PermissionDeniedException("You do not have permission to view this media asset.")

        return asset

    async def soft_delete_media_asset(
        self,
        user_id: str,
        is_admin: bool,
        asset_id: str,
        ip_address: str | None = None
    ) -> bool:
        """
        Soft-deletes a media asset record, enforcing owner/admin access.
        """
        asset = await self.media_repository.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise NotFoundException("Media asset record not found.")

        if asset.uploaded_by != user_id and not is_admin:
            raise PermissionDeniedException("You do not have permission to delete this media asset.")

        success = await self.media_repository.soft_delete(asset_id)
        if not success:
            raise BaseAppException("Failed to delete media asset.")

        # Update deleted_at in db
        await self.media_repository.update(
            asset_id,
            {"deleted_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}
        )

        await self.audit_service.log_action(
            action="DELETE_MEDIA_ASSET",
            target_collection="media_assets",
            user_id=user_id,
            target_id=asset_id,
            ip_address=ip_address
        )

        return True

    async def check_storage_health(self) -> bool:
        """
        Tests connection to the S3/R2 storage layer.
        """
        return storage_manager.check_health()
