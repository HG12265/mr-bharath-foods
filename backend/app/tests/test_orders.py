from datetime import UTC, datetime, timedelta
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
        "products": MagicMock(),
        "categories": MagicMock(),
        "carts": MagicMock(),
        "inventories": MagicMock(),
        "checkouts": MagicMock(),
        "orders": MagicMock(),
        "counters": MagicMock(),
        "audit_logs": MagicMock(),
        "customers": MagicMock(),
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


def create_mock_checkout_doc(
    checkout_id: str, status: str = "completed"
) -> dict[str, Any]:
    return {
        "_id": ObjectId(checkout_id),
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",  # Valid 24-char ObjectId string
        "guest_token": None,
        "email": "customer@example.test",
        "shipping_address": {
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
                "quantity": 2,
                "price": Decimal("200.00"),
                "reserved_warehouse_id": "WH-MAIN",
            }
        ],
        "subtotal": Decimal("400.00"),
        "tax_estimate": Decimal("20.00"),
        "shipping_fee": Decimal("50.00"),
        "discount": Decimal("0.00"),
        "grand_total": Decimal("470.00"),
        "status": status,
        "idempotency_key": "idemp-123",
        "is_deleted": False,
        "expires_at": datetime.now(UTC) + timedelta(minutes=15),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def create_mock_product_doc(
    product_id: str,
    sku: str = "ALM-GHEE-250ML",
    status: str = "active",
    is_deleted: bool = False,
) -> dict[str, Any]:
    return {
        "_id": product_id,
        "name": "Organic Almond Ghee",
        "slug": "organic-almond-ghee",
        "description": "Tasty organic ghee description.",
        "short_description": "Organic almond ghee short description.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "media_ids": [],
        "sourcing": {"region": "Tamil Nadu", "story": "Grass-fed cows."},
        "attributes": [],
        "variants": [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": sku,
                "title": "250ml",
                "volume_weight": "250ml",
                "price": Decimal("200.00"),
                "stock_status": "in_stock",
                "is_active": True,
            }
        ],
        "seo": {"meta_title": None, "meta_description": None, "meta_keywords": []},
        "ratings": {"average_rating": 4.5, "review_count": 5},
        "status": status,
        "is_deleted": is_deleted,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def create_mock_customer_doc(customer_id: str) -> dict[str, Any]:
    return {
        "_id": customer_id,
        "auth": {
            "email": "customer@example.test",
            "phone": "9876543210",
            "role": "customer",
            "status": "active",
        },
        "personal_details": {"first_name": "Gowtham", "last_name": "Dev"},
        "addresses": [],
        "is_deleted": False,
    }


def create_mock_order_doc(order_id: str, status: str = "pending_payment") -> dict[str, Any]:
    return {
        "_id": ObjectId(order_id),
        "order_number": "MBF-20260606-000042",
        "checkout_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",  # Valid 24-char ObjectId string
        "guest_token": None,
        "customer_snapshot": {
            "customer_id": "60c72b2f9b1d8e2a3c4f5e7b",
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
        "payment_status": "pending",
        "fulfillment_status": "pending",
        "order_status": status,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.mark.anyio
async def test_create_order_success(mock_db: MagicMock) -> None:
    checkout_id = "60c72b2f9b1d8e2a3c4f5e6e"
    checkout_doc = create_mock_checkout_doc(checkout_id, status="completed")
    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    customer_doc = create_mock_customer_doc("60c72b2f9b1d8e2a3c4f5e7b")

    mock_db["checkouts"].find_one = AsyncMock(return_value=checkout_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=None)
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["customers"].find_one = AsyncMock(return_value=customer_doc)
    mock_db["counters"].find_one_and_update = AsyncMock(return_value={"seq": 42})
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Capture insert data
    inserted_doc: dict[str, Any] = {}

    async def mock_insert(doc: dict[str, Any]) -> Any:
        inserted_doc.update(doc)
        inserted_doc["_id"] = ObjectId("60c72b2f9b1d8e2a3c4f5e7a")
        mock_result = MagicMock()
        mock_result.inserted_id = inserted_doc["_id"]
        return mock_result

    mock_db["orders"].insert_one = AsyncMock(side_effect=mock_insert)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/from-checkout/{checkout_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    today_str = datetime.now().strftime("%Y%m%d")
    assert res_data["data"]["order_number"] == f"MBF-{today_str}-000042"
    assert res_data["data"]["customer_snapshot"]["first_name"] == "Gowtham"
    assert res_data["data"]["items"][0]["product_name"] == "Organic Almond Ghee"
    assert res_data["data"]["items"][0]["variant_title"] == "250ml"
    assert Decimal(str(res_data["data"]["pricing"]["grand_total"])) == Decimal("470.00")
    assert res_data["data"]["order_status"] == "pending_payment"


@pytest.mark.anyio
async def test_create_order_duplicate_checkout(mock_db: MagicMock) -> None:
    checkout_id = "60c72b2f9b1d8e2a3c4f5e6e"
    checkout_doc = create_mock_checkout_doc(checkout_id, status="completed")
    order_doc = create_mock_order_doc("60c72b2f9b1d8e2a3c4f5e7a")

    mock_db["checkouts"].find_one = AsyncMock(return_value=checkout_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/from-checkout/{checkout_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already been created" in response.json()["message"]


@pytest.mark.anyio
async def test_create_order_incomplete_checkout(mock_db: MagicMock) -> None:
    checkout_id = "60c72b2f9b1d8e2a3c4f5e6e"
    checkout_doc = create_mock_checkout_doc(checkout_id, status="initiated")

    mock_db["checkouts"].find_one = AsyncMock(return_value=checkout_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=None)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/from-checkout/{checkout_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "status must be 'completed'" in response.json()["message"]


@pytest.mark.anyio
async def test_create_order_forbidden_owner(mock_db: MagicMock) -> None:
    checkout_id = "60c72b2f9b1d8e2a3c4f5e6e"
    checkout_doc = create_mock_checkout_doc(checkout_id, status="completed")

    mock_db["checkouts"].find_one = AsyncMock(return_value=checkout_doc)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e99", email="hacker@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/from-checkout/{checkout_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "Access forbidden" in response.json()["message"]


@pytest.mark.anyio
async def test_get_order_by_id_auth(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Case 1: Unauthorized customer attempts to fetch
    mock_user_unauth = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e99", email="hacker@mrbharathfoods.in", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user_unauth

    response1 = client.get(f"/api/v1/orders/{order_id}")
    assert response1.status_code == 403

    # Case 2: Authorized customer fetches
    mock_user_auth = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user_auth
    response2 = client.get(f"/api/v1/orders/{order_id}")
    assert response2.status_code == 200

    # Case 3: Admin fetches
    mock_admin = TokenData(
        user_id="admin_123", email="admin@mrbharathfoods.in", role=UserRole.ADMIN
    )
    app.dependency_overrides[get_optional_current_user] = lambda: mock_admin
    response3 = client.get(f"/api/v1/orders/{order_id}")
    assert response3.status_code == 200

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_my_order_history(mock_db: MagicMock) -> None:
    order_doc = create_mock_order_doc("60c72b2f9b1d8e2a3c4f5e7a")

    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [order_doc]
    mock_db["orders"].find = MagicMock(return_value=mock_cursor)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.get("/api/v1/orders/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["order_number"] == "MBF-20260606-000042"


@pytest.mark.anyio
async def test_admin_order_listing(mock_db: MagicMock) -> None:
    order_doc = create_mock_order_doc("60c72b2f9b1d8e2a3c4f5e7a")

    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__.return_value = [order_doc]
    mock_db["orders"].find = MagicMock(return_value=mock_cursor)

    # Warehouse role has clearance to view admin orders
    mock_warehouse = TokenData(
        user_id="wh_123", email="wh@mrbharathfoods.in", role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    response = client.get("/api/v1/admin/orders/")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 1


@pytest.mark.anyio
async def test_cancel_unpaid_order_success(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id, status="pending_payment")
    inventory_doc = {
        "_id": ObjectId("60c72b2f9b1d8e2a3c4f5e6a"),
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {"warehouse_id": "WH-MAIN", "on_hand": 10, "reserved": 2}
        ],
    }

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_doc)
    mock_db["inventories"].find_one_and_update = AsyncMock(return_value=inventory_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Track updates to order
    updated_doc = {}

    async def mock_update(filter_query: Any, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        updated_doc.update(order_doc)
        return order_doc

    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/{order_id}/cancel")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert response.json()["data"]["order_status"] == "cancelled"
    assert response.json()["data"]["fulfillment_status"] == "cancelled"

    # Verify inventory release was called
    mock_db["inventories"].find_one_and_update.assert_called()


@pytest.mark.anyio
async def test_cancel_paid_order_fails(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)
    order_doc["payment_status"] = "paid"

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)

    mock_user = TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e7b", email="customer@example.test", role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    response = client.post(f"/api/v1/orders/{order_id}/cancel")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Cannot cancel a paid order" in response.json()["message"]


@pytest.mark.anyio
async def test_admin_update_status_transitions(mock_db: MagicMock) -> None:
    order_id = "60c72b2f9b1d8e2a3c4f5e7a"
    order_doc = create_mock_order_doc(order_id)

    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    async def mock_update(filter_query: Any, update_payload: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_payload:
            order_doc.update(update_payload["$set"])
        return order_doc

    mock_db["orders"].find_one_and_update = AsyncMock(side_effect=mock_update)

    mock_admin = TokenData(
        user_id="admin_123", email="admin@mrbharathfoods.in", role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    # Case 1: Valid transition pending_payment -> confirmed
    response1 = client.patch(
        f"/api/v1/admin/orders/{order_id}/status", json={"order_status": "confirmed"}
    )
    assert response1.status_code == 200, response1.json()
    assert response1.json()["data"]["order_status"] == "confirmed"

    # Case 2: Invalid transition confirmed -> pending_payment
    response2 = client.patch(
        f"/api/v1/admin/orders/{order_id}/status", json={"order_status": "pending_payment"}
    )
    assert response2.status_code == 400
    assert "Invalid order status transition" in response2.json()["message"]

    app.dependency_overrides.clear()
