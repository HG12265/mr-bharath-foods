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
        "orders": MagicMock(),
        "shipments": MagicMock(),
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


def create_mock_order_doc(
    order_id: str, order_status: str = "confirmed", payment_status: str = "paid"
) -> dict[str, Any]:
    return {
        "_id": ObjectId(order_id),
        "order_number": "MBF-20260606-000042",
        "checkout_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "customer_id": "customer_123",
        "guest_token": None,
        "customer_snapshot": {
            "customer_id": "customer_123",
            "first_name": "Gowtham",
            "last_name": "Dev",
            "email": "customer@example.test",
            "phone": "9876543210",
        },
        "shipping_address_snapshot": {
            "full_name": "Gowtham Dev",
            "phone": "9876543210",
            "address_line1": "123 Main Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
            "country": "India",
        },
        "items": [],
        "pricing": {
            "subtotal": "400.00",
            "discount": "0.00",
            "tax_total": "20.00",
            "shipping_fee": "50.00",
            "grand_total": "470.00",
        },
        "payment_status": payment_status,
        "fulfillment_status": "pending",
        "order_status": order_status,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def create_mock_shipment_doc(shipment_id: str, order_id: str) -> dict[str, Any]:
    return {
        "_id": ObjectId(shipment_id),
        "order_id": order_id,
        "order_number": "MBF-20260606-000042",
        "customer_id": "customer_123",
        "carrier_name": "Delhivery",
        "tracking_number": "TRK12345",
        "awb_number": "AWB98765",
        "status": "pending",
        "timeline": [
            {
                "status": "pending",
                "message": "Shipment details created manually.",
                "timestamp": datetime.now(UTC),
                "location": None,
            }
        ],
        "shipped_at": None,
        "delivered_at": None,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.mark.anyio
async def test_create_shipment_success(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id, order_status="confirmed", payment_status="paid")

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["shipments"].find_one = AsyncMock(return_value=None)
    mock_db["audit_logs"].insert_one = AsyncMock()

    inserted_doc = {}

    async def mock_insert(doc: dict[str, Any]) -> Any:
        inserted_doc.update(doc)
        inserted_doc["_id"] = ObjectId("60c72b2f9b1d8e2a3c4f5e7d")
        mock_result = MagicMock()
        mock_result.inserted_id = inserted_doc["_id"]
        return mock_result

    mock_db["shipments"].insert_one = AsyncMock(side_effect=mock_insert)

    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    payload = {
        "carrier_name": "Delhivery",
        "tracking_number": "TRK12345",
        "awb_number": "AWB98765",
    }
    response = client.post(f"/api/v1/shipments/order/{order_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "pending"
    assert res_data["data"]["carrier_name"] == "Delhivery"
    assert len(res_data["data"]["timeline"]) == 1
    assert res_data["data"]["timeline"][0]["status"] == "pending"


@pytest.mark.anyio
async def test_create_shipment_unpaid_fails(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    # Order is pending payment (unpaid)
    order_doc = create_mock_order_doc(order_id, order_status="pending_payment", payment_status="pending")

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)

    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    payload = {
        "carrier_name": "Delhivery",
        "tracking_number": "TRK12345",
        "awb_number": "AWB98765",
    }
    response = client.post(f"/api/v1/shipments/order/{order_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "paid and confirmed" in response.json()["message"]


@pytest.mark.anyio
async def test_create_shipment_duplicate_fails(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id, order_status="confirmed", payment_status="paid")
    existing_shipment = create_mock_shipment_doc("60c72b2f9b1d8e2a3c4f5e7d", order_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["shipments"].find_one = AsyncMock(return_value=existing_shipment)

    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    payload = {
        "carrier_name": "Delhivery",
        "tracking_number": "TRK12345",
        "awb_number": "AWB98765",
    }
    response = client.post(f"/api/v1/shipments/order/{order_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already exists" in response.json()["message"]


@pytest.mark.anyio
async def test_update_status_timeline_append_and_sync(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    shipment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    shipment_doc = create_mock_shipment_doc(shipment_id, order_id)
    order_doc = create_mock_order_doc(order_id, order_status="confirmed", payment_status="paid")

    mock_db["shipments"].find_one = AsyncMock(return_value=shipment_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update_shipment(sid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            shipment_doc.update(update_payload["$set"])
        return shipment_doc

    async def mock_update_order(oid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        return order_doc

    mock_db["shipments"].find_one_and_update = AsyncMock(side_effect=mock_update_shipment)
    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update_order)

    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    # 1. Update to packed
    payload = {"status": "packed", "message": "Shipment packed in box.", "location": "Chennai Warehouse"}
    response = client.patch(f"/api/v1/admin/shipments/{shipment_id}/status", json=payload)
    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["data"]["status"] == "packed"
    assert len(res_data["data"]["timeline"]) == 2
    assert res_data["data"]["timeline"][1]["status"] == "packed"
    assert res_data["data"]["timeline"][1]["location"] == "Chennai Warehouse"
    assert order_doc["fulfillment_status"] == "packed"

    # 2. Update to shipped
    payload_shipped = {"status": "shipped", "message": "Dispatched via Delhivery.", "location": "Chennai Hub"}
    response_shipped = client.patch(f"/api/v1/admin/shipments/{shipment_id}/status", json=payload_shipped)
    assert response_shipped.status_code == 200
    assert response_shipped.json()["data"]["status"] == "shipped"
    assert order_doc["fulfillment_status"] == "shipped"
    assert response_shipped.json()["data"]["shipped_at"] is not None

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_customer_ownership_checks(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    shipment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    shipment_doc = create_mock_shipment_doc(shipment_id, order_id)

    mock_db["shipments"].find_one = AsyncMock(return_value=shipment_doc)

    # Authorized Customer (owner)
    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.get(f"/api/v1/shipments/{shipment_id}")
    assert response.status_code == 200, response.json()

    # Unauthorized Customer (different user ID)
    mock_other_customer = TokenData(
        user_id="customer_999", email="hacker@bharathdelight.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_current_user] = lambda: mock_other_customer
    response_forbidden = client.get(f"/api/v1/shipments/{shipment_id}")
    assert response_forbidden.status_code == 403

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_admin_listing_checks(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    shipment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    shipment_doc = create_mock_shipment_doc(shipment_id, order_id)

    # Mock cursor for find with chainable skip and limit methods
    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [shipment_doc]
    mock_db["shipments"].find = MagicMock(return_value=mock_cursor)

    # 1. Customer request fails
    mock_customer = TokenData(
        user_id="customer_123", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response_cust = client.get("/api/v1/admin/shipments/")
    assert response_cust.status_code == 403

    # 2. Warehouse request succeeds
    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse
    response_staff = client.get("/api/v1/admin/shipments/")
    assert response_staff.status_code == 200
    assert len(response_staff.json()["data"]) == 1

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_admin_edit_cancel_delete_shipment(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    shipment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    shipment_doc = create_mock_shipment_doc(shipment_id, order_id)
    order_doc = create_mock_order_doc(order_id, order_status="confirmed", payment_status="paid")

    mock_db["shipments"].find_one = AsyncMock(return_value=shipment_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update_shipment(sid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            shipment_doc.update(update_payload["$set"])
        return shipment_doc

    async def mock_update_order(oid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        return order_doc

    mock_db["shipments"].find_one_and_update = AsyncMock(side_effect=mock_update_shipment)
    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update_order)

    # 1. Non-admin fails to edit
    mock_warehouse = TokenData(
        user_id="staff_123", email="warehouse@bharathdelight.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    payload_edit = {
        "carrier_name": "DHL Express",
        "tracking_number": "TRK99999",
        "awb_number": None,
        "estimated_delivery_date": "2026-06-15T12:00:00Z"
    }
    response_edit_warehouse = client.patch(f"/api/v1/admin/shipments/{shipment_id}", json=payload_edit)
    assert response_edit_warehouse.status_code == 403

    # 2. Admin edits successfully
    mock_admin = TokenData(
        user_id="admin_123", email="admin@bharathdelight.in", role=UserRole.ADMIN
    )
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    response_edit_admin = client.patch(f"/api/v1/admin/shipments/{shipment_id}", json=payload_edit)
    assert response_edit_admin.status_code == 200, response_edit_admin.json()
    assert response_edit_admin.json()["data"]["carrier_name"] == "DHL Express"
    assert response_edit_admin.json()["data"]["tracking_number"] == "TRK99999"
    assert response_edit_admin.json()["data"]["awb_number"] is None
    assert response_edit_admin.json()["data"]["estimated_delivery_date"] is not None

    # 3. Admin cancels shipment successfully
    response_cancel = client.post(f"/api/v1/admin/shipments/{shipment_id}/cancel")
    assert response_cancel.status_code == 200
    assert response_cancel.json()["data"]["status"] == "cancelled"
    assert order_doc["fulfillment_status"] == "cancelled"

    # 4. Admin deletes shipment successfully
    response_delete = client.delete(f"/api/v1/admin/shipments/{shipment_id}")
    assert response_delete.status_code == 200
    assert response_delete.json()["success"] is True
    assert shipment_doc["is_deleted"] is True

    app.dependency_overrides.clear()

