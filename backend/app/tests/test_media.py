from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.schemas.auth import TokenData
from main import app

client = TestClient(app)


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_db() -> MagicMock:
    db = MagicMock()
    collections = {
        "media_assets": MagicMock(),
        "audit_logs": MagicMock(),
    }
    def get_mock_collection(key: str) -> MagicMock:
        if key not in collections:
            coll = MagicMock()
            coll.insert_one = AsyncMock()
            coll.find_one = AsyncMock(return_value=None)
            coll.find_one_and_update = AsyncMock(return_value=None)
            coll.update_many = AsyncMock()
            collections[key] = coll
        return collections[key]
    db.__getitem__.side_effect = get_mock_collection
    return db


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_token_data() -> TokenData:
    return TokenData(
        user_id="507f1f77bcf86cd799439011",
        email="test@bharathdelight.in",
        role=UserRole.CUSTOMER
    )


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_admin_token_data() -> TokenData:
    return TokenData(
        user_id="admin_user_id_12345",
        email="admin@bharathdelight.in",
        role=UserRole.ADMIN
    )


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_s3() -> Generator[MagicMock, None, None]:
    from app.core.storage import storage_manager
    mock_client = MagicMock()
    storage_manager._client = mock_client
    yield mock_client
    storage_manager._client = None


def test_request_presign_success(
    mock_db: MagicMock,
    mock_token_data: TokenData,
    mock_s3: MagicMock
) -> None:
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "public_url": "https://r2.com/mbf-media-bucket/media/avatar/uuid-avatar.png",
        "uploaded_by": "507f1f77bcf86cd799439011",
        "asset_type": "avatar",
        "status": "pending",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["media_assets"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439222"))
    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    mock_s3.generate_presigned_url = MagicMock(return_value="https://mock-r2-upload-url.com/put")

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    payload = {
        "filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "asset_type": "avatar"
    }

    response = client.post("/api/v1/media/presign", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["upload_url"] == "https://mock-r2-upload-url.com/put"
    assert json_data["data"]["id"] == "507f1f77bcf86cd799439222"


def test_request_presign_validation_failures(
    mock_db: MagicMock,
    mock_token_data: TokenData
) -> None:
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    # Test Case 1: Invalid File Extension (.exe is not permitted for avatar)
    payload_invalid_ext = {
        "filename": "malicious.exe",
        "content_type": "image/png",
        "size": 1024,
        "asset_type": "avatar"
    }
    response = client.post("/api/v1/media/presign", json=payload_invalid_ext)
    assert response.status_code == 400
    assert "extension" in response.json()["message"]

    # Test Case 2: File size too large (exceeds avatar 2MB limit)
    payload_too_large = {
        "filename": "huge_avatar.png",
        "content_type": "image/png",
        "size": 5 * 1024 * 1024,  # 5MB
        "asset_type": "avatar"
    }
    response = client.post("/api/v1/media/presign", json=payload_too_large)
    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["message"]

    app.dependency_overrides.clear()


def test_complete_upload_success(
    mock_db: MagicMock,
    mock_token_data: TokenData,
    mock_s3: MagicMock
) -> None:
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "public_url": "https://r2.com/mbf-media-bucket/media/avatar/uuid-avatar.png",
        "uploaded_by": "507f1f77bcf86cd799439011",
        "asset_type": "avatar",
        "status": "pending",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    # head_object mock doesn't raise exception (signifying file exists)
    mock_s3.head_object = MagicMock(return_value={})

    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)
    mock_db["media_assets"].find_one_and_update = AsyncMock(return_value={**asset_doc, "status": "completed"})
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    payload = {
        "id": "507f1f77bcf86cd799439222",
        "status": "completed"
    }

    response = client.post("/api/v1/media/complete", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "completed"


def test_complete_upload_file_missing_in_r2(
    mock_db: MagicMock,
    mock_token_data: TokenData,
    mock_s3: MagicMock
) -> None:
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "public_url": "https://r2.com/mbf-media-bucket/media/avatar/uuid-avatar.png",
        "uploaded_by": "507f1f77bcf86cd799439011",
        "asset_type": "avatar",
        "status": "pending",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    # head_object throws Exception (signifying file does not exist in R2 bucket)
    mock_s3.head_object = MagicMock(side_effect=Exception("NoSuchKey"))

    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    payload = {
        "id": "507f1f77bcf86cd799439222",
        "status": "completed"
    }

    response = client.post("/api/v1/media/complete", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "could not be found in storage" in response.json()["message"]


def test_complete_upload_permission_denied(
    mock_db: MagicMock,
    mock_token_data: TokenData
) -> None:
    # Asset uploaded by a different user
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/another_user_id_99999/uuid-avatar.png",
        "public_url": "https://r2.com/mbf-media-bucket/media/avatar/uuid-avatar.png",
        "uploaded_by": "another_user_id_99999",
        "asset_type": "avatar",
        "status": "pending",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    payload = {
        "id": "507f1f77bcf86cd799439222",
        "status": "completed"
    }

    response = client.post("/api/v1/media/complete", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "permission" in response.json()["message"]


def test_delete_media_asset_by_owner(
    mock_db: MagicMock,
    mock_token_data: TokenData
) -> None:
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "public_url": "https://r2.com/mbf-media-bucket/media/avatar/uuid-avatar.png",
        "uploaded_by": "507f1f77bcf86cd799439011",
        "asset_type": "avatar",
        "status": "completed",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)
    mock_db["media_assets"].update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_db["media_assets"].find_one_and_update = AsyncMock(return_value={**asset_doc, "is_deleted": True})
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    response = client.delete("/api/v1/media/507f1f77bcf86cd799439222")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_storage_provider_selection() -> None:
    from app.core.config import settings
    from app.core.storage import StorageManager

    manager = StorageManager()

    # Save original values
    orig_r2_endpoint = manager.endpoint_url
    orig_r2_access = manager.access_key_id
    orig_r2_secret = manager.secret_access_key
    orig_r2_bucket = manager.bucket_name
    orig_cloud_name = settings.CLOUDINARY_CLOUD_NAME
    orig_cloud_key = settings.CLOUDINARY_API_KEY
    orig_cloud_secret = settings.CLOUDINARY_API_SECRET

    try:
        # Case 1: All settings are placeholders -> fallback to local
        manager.endpoint_url = "https://account_id.r2.cloudflarestorage.com"
        manager.access_key_id = "r2_access_key"
        manager.secret_access_key = "r2_secret_key"
        manager.bucket_name = "mbf-media-bucket"

        settings.CLOUDINARY_CLOUD_NAME = "cloudinary_cloud_name"
        settings.CLOUDINARY_API_KEY = "cloudinary_api_key"
        settings.CLOUDINARY_API_SECRET = "cloudinary_api_secret"

        assert manager.storage_provider == "local"
        assert manager.use_local_storage is False

        # Case 2: Valid Cloudinary settings and placeholder R2 -> selects cloudinary
        settings.CLOUDINARY_CLOUD_NAME = "mycloud"
        settings.CLOUDINARY_API_KEY = "mykey"
        settings.CLOUDINARY_API_SECRET = "mysecret"

        assert manager.storage_provider == "cloudinary"
        assert manager.use_local_storage is True

        # Case 3: Valid R2 settings -> selects r2 (retaining priority over cloudinary)
        manager.endpoint_url = "https://real-account-id.r2.cloudflarestorage.com"
        manager.access_key_id = "real_access_key"
        manager.secret_access_key = "real_secret_key"
        manager.bucket_name = "real-bucket"

        assert manager.storage_provider == "r2"
        assert manager.use_local_storage is False

    finally:
        # Restore settings
        manager.endpoint_url = orig_r2_endpoint
        manager.access_key_id = orig_r2_access
        manager.secret_access_key = orig_r2_secret
        manager.bucket_name = orig_r2_bucket
        settings.CLOUDINARY_CLOUD_NAME = orig_cloud_name
        settings.CLOUDINARY_API_KEY = orig_cloud_key
        settings.CLOUDINARY_API_SECRET = orig_cloud_secret


def test_cloudinary_upload_mock_put(
    mock_db: MagicMock,
    mock_token_data: TokenData
) -> None:
    import unittest.mock as mock

    from app.core.config import settings

    # Configure mock cloudinary provider
    orig_cloud_name = settings.CLOUDINARY_CLOUD_NAME
    orig_cloud_key = settings.CLOUDINARY_API_KEY
    orig_cloud_secret = settings.CLOUDINARY_API_SECRET

    settings.CLOUDINARY_CLOUD_NAME = "real_cloud"
    settings.CLOUDINARY_API_KEY = "real_key"
    settings.CLOUDINARY_API_SECRET = "real_secret"

    # Mock database documents
    asset_doc = {
        "_id": "507f1f77bcf86cd799439222",
        "original_filename": "avatar.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "public_url": "http://localhost/static/media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
        "uploaded_by": "507f1f77bcf86cd799439011",
        "asset_type": "avatar",
        "status": "pending",
        "is_deleted": False
    }

    mock_db["media_assets"].find_one = AsyncMock(return_value=asset_doc)
    mock_db["media_assets"].update_one = AsyncMock(return_value=MagicMock(modified_count=1))

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    # Mock cloudinary upload call
    mock_cloudinary_res = {"secure_url": "https://res.cloudinary.com/real_cloud/image/upload/v1234/uuid-avatar.png"}

    with mock.patch("cloudinary.uploader.upload", return_value=mock_cloudinary_res) as mock_upload:
        # PUT request to mock endpoint
        response = client.put(
            "/api/v1/media/upload/mock/media/avatar/507f1f77bcf86cd799439011/uuid-avatar.png",
            content=b"dummy-image-bytes",
            headers={"Content-Type": "image/png"}
        )

        # Verify response
        assert response.status_code == 200
        json_res = response.json()
        assert json_res["success"] is True
        assert json_res["data"]["public_url"] == "https://res.cloudinary.com/real_cloud/image/upload/v1234/uuid-avatar.png"

        # Verify cloudinary upload call parameters
        mock_upload.assert_called_once()
        _, kwargs = mock_upload.call_args
        assert kwargs["folder"] == f"{settings.MEDIA_FOLDER_PREFIX}/avatar/507f1f77bcf86cd799439011"
        assert kwargs["public_id"] == "uuid-avatar"

        # Verify db update call
        mock_db["media_assets"].update_one.assert_called_once()
        db_args, _ = mock_db["media_assets"].update_one.call_args
        assert db_args[1]["$set"]["public_url"] == "https://res.cloudinary.com/real_cloud/image/upload/v1234/uuid-avatar.png"

    # Restore settings
    settings.CLOUDINARY_CLOUD_NAME = orig_cloud_name
    settings.CLOUDINARY_API_KEY = orig_cloud_key
    settings.CLOUDINARY_API_SECRET = orig_cloud_secret
    app.dependency_overrides.clear()
