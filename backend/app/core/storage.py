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
    def client(self) -> Any:
        if not self._client:
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

    def verify_object_exists(self, key: str) -> bool:
        """
        Queries R2 using head_object to verify if key has been uploaded successfully.
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def delete_object(self, key: str) -> bool:
        """
        Deletes object associated with key in the bucket.
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def check_health(self) -> bool:
        """
        Validates connection to R2 by performing list query with MaxKeys=1.
        """
        try:
            self.client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            return True
        except Exception:
            return False


storage_manager = StorageManager()
