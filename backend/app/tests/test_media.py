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
    db["media_assets"] = MagicMock()
    db["audit_logs"] = MagicMock()
    return db


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_token_data() -> TokenData:
    return TokenData(
        user_id="507f1f77bcf86cd799439011",
        email="test@mrbharathfoods.in",
        role=UserRole.CUSTOMER
    )


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_admin_token_data() -> TokenData:
    return TokenData(
        user_id="admin_user_id_12345",
        email="admin@mrbharathfoods.in",
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
