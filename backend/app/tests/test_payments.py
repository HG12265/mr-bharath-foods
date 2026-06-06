from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.v1.carts import get_optional_current_user
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
        "payments": MagicMock(),
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


def create_mock_order_doc(order_id: str, payment_status: str = "pending") -> dict[str, Any]:
    return {
        "_id": ObjectId(order_id),
        "order_number": "MBF-20260606-000042",
        "checkout_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "guest_token": None,
        "customer_snapshot": {
            "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",
            "first_name": "Gowtham",
            "last_name": "Dev",
            "email": "customer@mrbharathfoods.in",
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
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "product_name": "Organic Almond Ghee",
                "variant_title": "250ml",
                "quantity": 2,
                "unit_price": Decimal("200.00"),
                "line_total": Decimal("400.00"),
                "reserved_warehouse_id": "WH-MAIN",
            }
        ],
        "pricing": {
            "subtotal": Decimal("400.00"),
            "discount": Decimal("0.00"),
            "tax_total": Decimal("20.00"),
            "shipping_fee": Decimal("50.00"),
            "grand_total": Decimal("470.00"),
        },
        "payment_status": payment_status,
        "fulfillment_status": "pending",
        "order_status": "pending_payment",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def create_mock_payment_doc(payment_id: str, status: str = "pending") -> dict[str, Any]:
    return {
        "_id": ObjectId(payment_id),
        "order_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "order_number": "MBF-20260606-000042",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "guest_token": None,
        "amount": Decimal("470.00"),
        "upi_id": "mrbharathfoods@upi",
        "upi_link": "upi://pay?pa=mrbharathfoods@upi&pn=MR%20BHARATH%20FOODS&am=470.00&cu=INR&tn=MBF-20260606-000042",
        "status": status,
        "screenshot_media_id": None,
        "transaction_note": "Order MBF-20260606-000042",
        "rejection_reason": None,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def create_mock_media_doc(media_id: str, uploaded_by: str = "60c72b2f9b1d8e2a3c4f5e7b") -> dict[str, Any]:
    return {
        "_id": ObjectId(media_id),
        "original_filename": "receipt.png",
        "content_type": "image/png",
        "size": 1024 * 1024,  # 1MB
        "storage_key": "payment_proofs/receipt.png",
        "public_url": "https://r2.mrbharathfoods.in/payment_proofs/receipt.png",
        "uploaded_by": uploaded_by,
        "asset_type": "payment_proof",
        "status": "completed",
        "is_deleted": False,
    }


@pytest.mark.anyio
async def test_initiate_payment_success(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["payments"].find_one = AsyncMock(return_value=None)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Capture insert data
    inserted_doc = {}

    async def mock_insert(doc: dict[str, Any]) -> Any:
        inserted_doc.update(doc)
        inserted_doc["_id"] = ObjectId("60c72b2f9b1d8e2a3c4f5e7d")
        mock_result = MagicMock()
        mock_result.inserted_id = inserted_doc["_id"]
        return mock_result

    mock_db["payments"].insert_one = AsyncMock(side_effect=mock_insert)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/payments/order/{order_id}/initiate")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "pending"
    assert "upi://pay?pa=" in res_data["data"]["upi_link"]
    assert "am=470.00" in res_data["data"]["upi_link"]
    assert "tn=MBF-20260606-000042" in res_data["data"]["upi_link"]


@pytest.mark.anyio
async def test_initiate_payment_unauthorized_fails(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)

    # Different user
    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e99", email="hacker@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/payments/order/{order_id}/initiate")
    app.dependency_overrides.clear()

    assert response.status_code == 403


@pytest.mark.anyio
async def test_submit_payment_proof_success(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)
    payment_doc = create_mock_payment_doc("60c72b2f9b1d8e2a3c4f5e7d")
    media_id = "60c72b2f9b1d8e2a3c4f5e7c"
    media_doc = create_mock_media_doc(media_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["payments"].find_one = AsyncMock(return_value=payment_doc)
    mock_db["media_assets"].find_one = AsyncMock(return_value=media_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update(filter_query: Any, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            payment_doc.update(update_payload["$set"])
        return payment_doc

    mock_db["payments"].find_one_and_update = AsyncMock(side_effect=mock_update)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    payload = {"screenshot_media_id": media_id}
    response = client.post(f"/api/v1/payments/order/{order_id}/submit-proof", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert response.json()["data"]["status"] == "proof_submitted"
    assert response.json()["data"]["screenshot_media_id"] == media_id


@pytest.mark.anyio
async def test_submit_payment_proof_validation_failures(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)
    payment_doc = create_mock_payment_doc("60c72b2f9b1d8e2a3c4f5e7d")
    media_id = "60c72b2f9b1d8e2a3c4f5e7c"

    # Case 1: Media is not completed (e.g. status = pending)
    incomplete_media_doc = create_mock_media_doc(media_id)
    incomplete_media_doc["status"] = "pending"

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["payments"].find_one = AsyncMock(return_value=payment_doc)
    mock_db["media_assets"].find_one = AsyncMock(return_value=incomplete_media_doc)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    payload = {"screenshot_media_id": media_id}
    response = client.post(f"/api/v1/payments/order/{order_id}/submit-proof", json=payload)
    assert response.status_code == 400
    assert "upload has not completed" in response.json()["message"]

    # Case 2: Media asset format is wrong (e.g. image/gif)
    wrong_format_media = create_mock_media_doc(media_id)
    wrong_format_media["content_type"] = "image/gif"
    mock_db["media_assets"].find_one = AsyncMock(return_value=wrong_format_media)

    response2 = client.post(f"/api/v1/payments/order/{order_id}/submit-proof", json=payload)
    assert response2.status_code == 400
    assert "Unsupported format" in response2.json()["message"]

    # Case 3: Media belongs to another user
    wrong_owner_media = create_mock_media_doc(media_id, uploaded_by="60c72b2f9b1d8e2a3c4f5e99")
    mock_db["media_assets"].find_one = AsyncMock(return_value=wrong_owner_media)

    response3 = client.post(f"/api/v1/payments/order/{order_id}/submit-proof", json=payload)
    assert response3.status_code == 403
    assert "Access forbidden" in response3.json()["message"]

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_admin_payment_approval(mock_db: MagicMock) -> None:
    payment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    payment_doc = create_mock_payment_doc(payment_id, status="proof_submitted")
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["payments"].find_one = AsyncMock(return_value=payment_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update_payment(pid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            payment_doc.update(update_payload["$set"])
        return payment_doc

    async def mock_update_order(oid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        return order_doc

    mock_db["payments"].find_one_and_update = AsyncMock(side_effect=mock_update_payment)
    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update_order)

    mock_admin = TokenData(
        user_id="admin_123", email="admin@mrbharathfoods.in", role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    payload = {"action": "approve"}
    response = client.post(f"/api/v1/admin/payments/{payment_id}/verify", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert response.json()["data"]["status"] == "approved"
    assert response.json()["data"]["order_status"] == "confirmed"
    assert response.json()["data"]["payment_status"] == "paid"


@pytest.mark.anyio
async def test_admin_payment_rejection(mock_db: MagicMock) -> None:
    payment_id = "60c72b2f9b1d8e2a3c4f5e7d"
    payment_doc = create_mock_payment_doc(payment_id, status="proof_submitted")
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["payments"].find_one = AsyncMock(return_value=payment_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update_payment(pid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            payment_doc.update(update_payload["$set"])
        return payment_doc

    async def mock_update_order(oid: str, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        return order_doc

    mock_db["payments"].find_one_and_update = AsyncMock(side_effect=mock_update_payment)
    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update_order)

    mock_admin = TokenData(
        user_id="admin_123", email="admin@mrbharathfoods.in", role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    # Case 1: Rejection fails if reason is missing
    payload = {"action": "reject"}
    response1 = client.post(f"/api/v1/admin/payments/{payment_id}/verify", json=payload)
    assert response1.status_code == 400
    assert "reason is required" in response1.json()["message"]

    # Case 2: Rejection success with reason
    payload = {"action": "reject", "rejection_reason": "Receipt blurry."}
    response2 = client.post(f"/api/v1/admin/payments/{payment_id}/verify", json=payload)
    app.dependency_overrides.clear()

    assert response2.status_code == 200, response2.json()
    assert response2.json()["data"]["status"] == "rejected"
    assert response2.json()["data"]["order_status"] == "pending_payment"
    assert response2.json()["data"]["payment_status"] == "pending"
    assert payment_doc["rejection_reason"] == "Receipt blurry."
