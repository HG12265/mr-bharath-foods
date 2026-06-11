from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.schemas.auth import TokenData
from main import app

client = TestClient(app)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    collections = {
        "notifications": MagicMock(),
        "audit_logs": MagicMock(),
    }
    db.__getitem__.side_effect = lambda key: collections.setdefault(key, MagicMock())
    return db


def create_mock_notification_doc(
    notification_id: str,
    target_user_id: str | None = None,
    role_target: str | None = None,
    is_read: bool = False,
    noti_type: str = "order_created",
) -> dict[str, Any]:
    return {
        "_id": ObjectId(notification_id),
        "target_user_id": target_user_id,
        "role_target": role_target,
        "type": noti_type,
        "title": "Test Notification",
        "message": "This is a test notification message.",
        "metadata": {"order_id": "60c72b2f9b1d8e2a3c4f5e7a"},
        "is_read": is_read,
        "read_at": None,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.mark.anyio
async def test_create_notification_success(mock_db: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_db["audit_logs"].insert_one = AsyncMock()

    inserted_doc = {}

    async def mock_insert(doc: dict[str, Any]) -> Any:
        inserted_doc.update(doc)
        inserted_doc["_id"] = ObjectId("60c72b2f9b1d8e2a3c4f5e7d")
        mock_result = MagicMock()
        mock_result.inserted_id = inserted_doc["_id"]
        return mock_result

    mock_db["notifications"].insert_one = AsyncMock(side_effect=mock_insert)

    from app.repositories.notification_repository import NotificationRepository
    from app.services.audit_service import AuditService
    from app.services.notification_service import NotificationService

    repo = NotificationRepository(mock_db)
    audit_service = AuditService(MagicMock())
    mock_log_action = AsyncMock()
    monkeypatch.setattr(audit_service, "log_action", mock_log_action)

    service = NotificationService(repo, audit_service)

    notification = await service.create_notification(
        type="order_created",
        title="Order Created Successfully",
        message="Your order MBF-12345 has been created.",
        target_user_id="customer_123",
        metadata={"order_id": "60c72b2f9b1d8e2a3c4f5e7a"},
    )

    assert notification.target_user_id == "customer_123"
    assert notification.type == "order_created"
    assert notification.is_read is False
    assert notification.metadata["order_id"] == "60c72b2f9b1d8e2a3c4f5e7a"
    mock_log_action.assert_called_once()


@pytest.mark.anyio
async def test_list_customer_notifications(mock_db: MagicMock) -> None:
    noti_id = "60c72b2f9b1d8e2a3c4f5e7d"
    # Create notification targeted directly to customer_123
    noti_doc = create_mock_notification_doc(noti_id, target_user_id="customer_123")

    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [noti_doc]
    mock_db["notifications"].find = MagicMock(return_value=mock_cursor)

    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.get("/api/v1/notifications/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["target_user_id"] == "customer_123"


@pytest.mark.anyio
async def test_role_target_notification_visibility(mock_db: MagicMock) -> None:
    noti_id = "60c72b2f9b1d8e2a3c4f5e7d"
    # Notification targeted to role warehouse
    noti_doc = create_mock_notification_doc(noti_id, role_target="warehouse", noti_type="low_stock_alert")

    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [noti_doc]
    mock_db["notifications"].find = MagicMock(return_value=mock_cursor)

    # Warehouse staff request
    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@mrbharathfoods.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    response = client.get("/api/v1/notifications/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["role_target"] == "warehouse"


@pytest.mark.anyio
async def test_mark_notification_as_read(mock_db: MagicMock) -> None:
    noti_id = "60c72b2f9b1d8e2a3c4f5e7d"
    noti_doc = create_mock_notification_doc(noti_id, target_user_id="customer_123")

    mock_db["notifications"].find_one = AsyncMock(return_value=noti_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update(filter_query: Any, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            noti_doc.update(update_payload["$set"])
        return noti_doc

    mock_db["notifications"].find_one_and_update = AsyncMock(side_effect=mock_update)

    # 1. Customer read success
    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.patch(f"/api/v1/notifications/{noti_id}/read")
    assert response.status_code == 200, response.json()
    assert response.json()["data"]["is_read"] is True

    # 2. Other customer read forbidden
    mock_other_customer = TokenData(
        user_id="customer_999", email="hacker@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_current_user] = lambda: mock_other_customer
    response_forbidden = client.patch(f"/api/v1/notifications/{noti_id}/read")
    assert response_forbidden.status_code == 403

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_mark_all_notifications_as_read(mock_db: MagicMock) -> None:
    mock_db["notifications"].update_many = AsyncMock()
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Mock return count
    mock_result = MagicMock()
    mock_result.modified_count = 5
    mock_db["notifications"].update_many.return_value = mock_result

    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    # Check read-all endpoint
    response = client.patch("/api/v1/notifications/read-all")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert response.json()["data"]["modified_count"] == 5


@pytest.mark.anyio
async def test_admin_notifications_listing_access(mock_db: MagicMock) -> None:
    noti_id = "60c72b2f9b1d8e2a3c4f5e7d"
    noti_doc = create_mock_notification_doc(noti_id, target_user_id="customer_123")

    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [noti_doc]
    mock_db["notifications"].find = MagicMock(return_value=mock_cursor)

    # 1. Customer listing access forbidden
    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response_cust = client.get("/api/v1/admin/notifications")
    assert response_cust.status_code == 403

    # 2. Warehouse staff listing access allowed
    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@mrbharathfoods.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse
    response_staff = client.get("/api/v1/admin/notifications")
    app.dependency_overrides.clear()

    assert response_staff.status_code == 200
    assert len(response_staff.json()["data"]) == 1
