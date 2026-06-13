from typing import Any

from botocore.config import Config

from app.core.config import settings
from app.core.exceptions import BaseAppException


class StorageManager:
    def __init__(self) -> None:
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self.access_key_id = settings.R2_ACCESS_KEY_ID
        self.secret_access_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self._client: Any = None

    @property
    def storage_provider(self) -> str:
        # If client is mock-injected (e.g. in tests) or already active, default to r2
        if self._client is not None:
            return "r2"
        # Check R2 credentials
        if (
            self.endpoint_url
            and self.access_key_id
            and self.secret_access_key
            and self.bucket_name
            and "account_id" not in self.endpoint_url
            and self.access_key_id != "r2_access_key"
            and self.secret_access_key != "r2_secret_key"
            and self.endpoint_url.strip() != ""
            and self.access_key_id.strip() != ""
            and self.secret_access_key.strip() != ""
            and self.bucket_name.strip() != ""
        ):
            return "r2"

        # Check Cloudinary credentials
        if (
            settings.CLOUDINARY_CLOUD_NAME
            and settings.CLOUDINARY_API_KEY
            and settings.CLOUDINARY_API_SECRET
            and settings.CLOUDINARY_CLOUD_NAME != "cloudinary_cloud_name"
            and settings.CLOUDINARY_API_KEY != "cloudinary_api_key"
            and settings.CLOUDINARY_API_SECRET != "cloudinary_api_secret"
            and settings.CLOUDINARY_CLOUD_NAME.strip() != ""
            and settings.CLOUDINARY_API_KEY.strip() != ""
            and settings.CLOUDINARY_API_SECRET.strip() != ""
        ):
            return "cloudinary"

        # Fallback to local
        return "local"

    @property
    def use_local_storage(self) -> bool:
        if self._client is not None:
            return False
        return self.storage_provider == "cloudinary"

    @property
    def client(self) -> Any:
        if not self._client:
            if self.use_local_storage:
                raise BaseAppException(
                    message="Cloudflare R2 credentials not configured. Using alternative storage fallback.",
                    code="STORAGE_CONFIG_ERROR",
                    status_code=500
                )
            if not all([self.endpoint_url, self.access_key_id, self.secret_access_key, self.bucket_name]):
                raise BaseAppException(
                    message="Cloudflare R2 storage credentials are not fully configured in environment.",
                    code="STORAGE_CONFIG_ERROR",
                    status_code=500
                )

            import boto3
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto"
            )
        return self._client

    def generate_presigned_put_url(self, key: str, content_type: str, expires_in: int = 3600) -> str:
        """
        Generates a secure presigned PUT URL for direct frontend file uploads to R2.
        """
        if self.use_local_storage:
            return f"/api/v1/media/upload/mock/{key}"
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ContentType": content_type
                },
                ExpiresIn=expires_in
            )
            return str(url)
        except Exception as exc:
            raise BaseAppException(
                message=f"Failed to generate presigned upload URL: {exc!s}",
                code="PRESIGNED_URL_GENERATION_FAILED",
                status_code=500
            ) from exc

    async def verify_object_exists(self, key: str) -> bool:
        """
        Queries storage to verify if key has been uploaded successfully.
        """
        if self.storage_provider == "local":
            return False
        elif self.storage_provider == "cloudinary":
            try:
                from app.core.database import db_manager
                if db_manager.db is not None:
                    asset = await db_manager.db["media_assets"].find_one({"storage_key": key, "is_deleted": False})
                    if asset and asset.get("public_url") and "cloudinary.com" in asset["public_url"]:
                        return True
            except Exception:
                pass
            return False

        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def delete_object(self, key: str) -> bool:
        """
        Deletes object associated with key in the bucket/cloudinary/local storage.
        """
        if self.storage_provider == "local":
            return False
        elif self.storage_provider == "cloudinary":
            import os
            import re
            try:
                parts = key.split("/")
                # key: media/{asset_type}/{user_id}/{filename}
                asset_type = parts[1] if len(parts) > 1 else "misc"
                user_id = parts[2] if len(parts) > 2 else "anonymous"

                filename_with_ext = parts[-1]
                filename_base, _ = os.path.splitext(filename_with_ext)
                public_id = re.sub(r'[^a-zA-Z0-9._-]', '_', filename_base)

                folder_old = f"mr-bharath-foods/{asset_type}/{user_id}"
                full_public_id_old = f"{folder_old}/{public_id}"

                folder_new = f"{settings.MEDIA_FOLDER_PREFIX}/{asset_type}/{user_id}"
                full_public_id_new = f"{folder_new}/{public_id}"

                import cloudinary
                import cloudinary.uploader
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True
                )
                cloudinary.uploader.destroy(full_public_id_old)
                cloudinary.uploader.destroy(full_public_id_new)
                return True
            except Exception:
                return False

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def check_health(self) -> bool:
        """
        Validates connection to storage.
        """
        if self.storage_provider == "local":
            return False
        if self.use_local_storage:
            return True
        try:
            self.client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            return True
        except Exception:
            return False


storage_manager = StorageManager()
