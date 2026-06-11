from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_db
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


@pytest.mark.anyio
async def test_initiate_checkout_success(mock_db: MagicMock) -> None:
    cart_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "cust_123",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("200.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")

    inventory_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 50,
                "reserved": 0,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    checkout_state: dict[str, Any] = {}

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        # Determine based on shape of query
        if "idempotency_key" in filter_query:
            return checkout_state if checkout_state else None
        if "customer_id" in filter_query or "_id" in filter_query:
            return cart_doc
        return None

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        # Simulate inventory update or checkout update
        return inventory_doc

    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_doc)
    mock_db["inventories"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["checkouts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["checkouts"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6e")
    )
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "idempotency_key": "idemp-key-123",
    }

    # First attempt - Initiate
    response = client.post("/api/v1/checkouts/initiate", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    # Subtotal = 200 * 2 = 400. Tax = 5% = 20. Shipping = 50 (since subtotal < 500). Grand total = 470
    assert Decimal(str(json_data["data"]["pricing"]["subtotal"])) == Decimal("400.00")
    assert Decimal(str(json_data["data"]["pricing"]["tax_estimate"])) == Decimal("20.00")
    assert Decimal(str(json_data["data"]["pricing"]["shipping_fee"])) == Decimal("50.00")
    assert Decimal(str(json_data["data"]["pricing"]["grand_total"])) == Decimal("470.00")
    assert json_data["data"]["status"] == "initiated"

    # Save to mock subsequent idempotency check
    checkout_state.update(json_data["data"])
    # Convert id back to BSON structure mockup for get_by_idempotency_key
    checkout_state["_id"] = "60c72b2f9b1d8e2a3c4f5e6e"
    # Ensure expires_at etc are datetimes when model validating, we mock the repo layer conversion:
    checkout_state["expires_at"] = datetime.now(UTC) + timedelta(minutes=15)
    checkout_state["created_at"] = datetime.now(UTC)
    checkout_state["updated_at"] = datetime.now(UTC)
    checkout_state["shipping_address"]["country"] = "India"
    # Convert decimal fields inside pricing
    checkout_state["subtotal"] = Decimal("400.00")
    checkout_state["tax_estimate"] = Decimal("20.00")
    checkout_state["shipping_fee"] = Decimal("50.00")
    checkout_state["discount"] = Decimal("0.00")
    checkout_state["grand_total"] = Decimal("470.00")
    checkout_state["items"] = [
        {
            "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
            "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
            "sku": "ALM-GHEE-250ML",
            "quantity": 2,
            "price": Decimal("200.00"),
            "reserved_warehouse_id": "WH-MAIN",
        }
    ]

    # Second attempt - Idempotent reuse
    response2 = client.post("/api/v1/checkouts/initiate", json=payload)
    app.dependency_overrides.clear()

    assert response2.status_code == 200
    assert response2.json()["data"]["id"] == json_data["data"]["id"]


@pytest.mark.anyio
async def test_initiate_checkout_empty_cart(mock_db: MagicMock) -> None:
    cart_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "cust_123",
        "items": [],  # empty cart
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)
    mock_db["checkouts"].find_one = AsyncMock(return_value=None)
    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "idempotency_key": "idemp-key-123",
    }

    response = client.post("/api/v1/checkouts/initiate", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Cart must not be empty" in response.json()["message"]


@pytest.mark.anyio
async def test_initiate_checkout_validation_failures(mock_db: MagicMock) -> None:
    cart_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "cust_123",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("200.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)
    mock_db["checkouts"].find_one = AsyncMock(return_value=None)
    app.dependency_overrides[get_db] = lambda: mock_db

    # 1. Invalid Pincode
    payload: dict[str, Any] = {
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "email": "customer@example.test",
        "shipping_address": {
            "full_name": "Gowtham Dev",
            "phone": "9876543210",
            "address_line1": "123 Main Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "60001",  # 5 digits (invalid)
            "country": "India",
        },
        "idempotency_key": "idemp-key-123",
    }
    response = client.post("/api/v1/checkouts/initiate", json=payload)
    assert response.status_code == 400
    assert "Pincode must be exactly 6 digits" in response.json()["message"]

    # 2. Invalid Phone
    payload["shipping_address"]["pincode"] = "600001"
    payload["shipping_address"]["phone"] = "98765"  # too short
    response = client.post("/api/v1/checkouts/initiate", json=payload)
    assert response.status_code == 400
    assert "Phone number must contain at least 10 digits" in response.json()["message"]

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_initiate_checkout_insufficient_stock(mock_db: MagicMock) -> None:
    cart_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "cust_123",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 10,  # requesting 10
                "unit_price_snapshot": Decimal("200.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")

    inventory_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 5,  # only 5 available
                "reserved": 0,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 1,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_doc)
    mock_db["checkouts"].find_one = AsyncMock(return_value=None)
    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "idempotency_key": "idemp-key-123",
    }

    response = client.post("/api/v1/checkouts/initiate", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["message"]


@pytest.mark.anyio
async def test_apply_coupon_welcome10_success(mock_db: MagicMock) -> None:
    checkout_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "status": "initiated",
        "idempotency_key": "idemp-123",
        "expires_at": datetime.now(UTC) + timedelta(minutes=15),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return checkout_doc

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        if "$set" in update_doc:
            checkout_doc.update(update_doc["$set"])
        return checkout_doc

    mock_db["checkouts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["checkouts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/v1/checkouts/60c72b2f9b1d8e2a3c4f5e6e/apply-coupon",
        json={"coupon_code": "WELCOME10"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    # Subtotal = 400. Discount = 10% = 40.00. Net Subtotal = 360.
    # Tax = 5% of 360 = 18.00. Shipping = 50. Grand Total = 360 + 18 + 50 = 428
    assert Decimal(str(json_data["data"]["pricing"]["discount"])) == Decimal("40.00")
    assert Decimal(str(json_data["data"]["pricing"]["tax_estimate"])) == Decimal("18.00")
    assert Decimal(str(json_data["data"]["pricing"]["grand_total"])) == Decimal("428.00")


@pytest.mark.anyio
async def test_complete_checkout_success(mock_db: MagicMock) -> None:
    checkout_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "items": [],
        "subtotal": Decimal("400.00"),
        "tax_estimate": Decimal("20.00"),
        "shipping_fee": Decimal("50.00"),
        "discount": Decimal("0.00"),
        "grand_total": Decimal("470.00"),
        "status": "initiated",
        "idempotency_key": "idemp-123",
        "expires_at": datetime.now(UTC) + timedelta(minutes=15),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return checkout_doc

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        if "$set" in update_doc:
            checkout_doc.update(update_doc["$set"])
        return checkout_doc

    mock_db["checkouts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["checkouts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/v1/checkouts/60c72b2f9b1d8e2a3c4f5e6e/complete", json={"payment_method": "cod"}
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "completed"


@pytest.mark.anyio
async def test_complete_checkout_expired_releases_stock(mock_db: MagicMock) -> None:
    checkout_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "cart_id": "60c72b2f9b1d8e2a3c4f5e6f",
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
        "status": "initiated",
        "idempotency_key": "idemp-123",
        "expires_at": datetime.now(UTC) - timedelta(minutes=1),  # already expired 1 minute ago!
        "created_at": datetime.now(UTC) - timedelta(minutes=16),
        "updated_at": datetime.now(UTC) - timedelta(minutes=16),
    }

    inventory_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 50,
                "reserved": 2,  # 2 reserved
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        # Check shape of query
        if "sku" in filter_query:
            return inventory_doc
        return checkout_doc

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        # Simulate status update to expired
        if "$set" in update_doc:
            checkout_doc.update(update_doc["$set"])
        return checkout_doc

    mock_db["checkouts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["checkouts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["inventories"].find_one = AsyncMock(side_effect=mock_find_one)
    # The release of stock will update inventory in DB
    mock_db["inventories"].find_one_and_update = AsyncMock(return_value=inventory_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/v1/checkouts/60c72b2f9b1d8e2a3c4f5e6e/complete", json={"payment_method": "cod"}
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "expired" in response.json()["message"]
    # Verify checkout status was set to expired
    assert checkout_doc["status"] == "expired"
