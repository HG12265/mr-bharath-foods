from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
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
        "products": MagicMock(),
        "categories": MagicMock(),
        "inventories": MagicMock(),
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


@pytest.fixture
def mock_warehouse_token() -> TokenData:
    return TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e6d",
        email="warehouse@bharathdelight.in",
        role=UserRole.WAREHOUSE,
    )


@pytest.fixture
def mock_customer_token() -> TokenData:
    return TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e6e",
        email="customer@example.test",
        role=UserRole.CUSTOMER,
    )


@pytest.fixture
def mock_admin_token() -> TokenData:
    return TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e6a",
        email="admin@bharathdelight.in",
        role=UserRole.ADMIN,
    )


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
        "description": "Tasty organic almond ghee description.",
        "short_description": "Organic almond ghee short description.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "media_ids": ["60c72b2f9b1d8e2a3c4f5e6d"],
        "sourcing": {"region": "Tamil Nadu", "story": "Grass-fed cows."},
        "attributes": [],
        "variants": [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": sku,
                "title": "250ml",
                "volume_weight": "250ml",
                "price": Decimal("299.00"),
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
async def test_role_authorization_failed(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    # 1. Unauthenticated request
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/inventories/ALM-GHEE-250ML")
    assert response.status_code == 401

    # 2. Authenticated but insufficient permission (Customer role)
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token
    response = client.get("/api/v1/inventories/ALM-GHEE-250ML")
    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.anyio
async def test_create_inventory_success(
    mock_db: MagicMock, mock_admin_token: TokenData
) -> None:
    # Pre-checks — POST /inventories is ADMIN only
    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["inventories"].find_one = AsyncMock(return_value=None)
    mock_db["inventories"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6f")
    )
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token

    payload = {
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 100,
                "reserved": 0,
                "location_code": "A-12",
            }
        ],
        "safety_stock_level": 10,
    }

    response = client.post("/api/v1/inventories", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["sku"] == "ALM-GHEE-250ML"
    assert json_data["data"]["on_hand_total"] == 100
    assert json_data["data"]["reserved_total"] == 0
    assert json_data["data"]["available_total"] == 100
    assert json_data["data"]["is_low_stock"] is False
    assert json_data["data"]["inventory_status"] == "healthy"


@pytest.mark.anyio
async def test_create_inventory_duplicate(
    mock_db: MagicMock, mock_admin_token: TokenData
) -> None:
    # POST /inventories is ADMIN only
    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    existing_inventory = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    mock_db["inventories"].find_one = AsyncMock(return_value=existing_inventory)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token

    payload = {
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [],
        "safety_stock_level": 5,
    }

    response = client.post("/api/v1/inventories", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already exists" in response.json()["message"]


@pytest.mark.anyio
async def test_get_inventory_by_sku_success(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    inventory_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 50,
                "reserved": 10,
                "location_code": "B-3",
            },
            {
                "warehouse_id": "WH-NORTH",
                "on_hand": 20,
                "reserved": 5,
                "location_code": "C-1",
            },
        ],
        "safety_stock_level": 60,  # total available = 40 + 15 = 55 < 60, should trigger low stock alert
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    response = client.get("/api/v1/inventories/ALM-GHEE-250ML")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["on_hand_total"] == 70
    assert json_data["data"]["reserved_total"] == 15
    assert json_data["data"]["available_total"] == 55
    assert json_data["data"]["is_low_stock"] is True


@pytest.mark.anyio
async def test_stock_adjustment_success(
    mock_db: MagicMock, mock_admin_token: TokenData
) -> None:
    # PATCH /adjust is ADMIN only
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 20,
                "reserved": 5,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return inventory_state

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        if "$set" in update_doc:
            inventory_state.update(update_doc["$set"])
        return inventory_state

    mock_db["inventories"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["inventories"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": 15, "location_code": "A-1-UPDATED"}
    response = client.patch("/api/v1/inventories/ALM-GHEE-250ML/adjust", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["warehouse_stock"][0]["on_hand"] == 35
    assert json_data["data"]["warehouse_stock"][0]["location_code"] == "A-1-UPDATED"


@pytest.mark.anyio
async def test_stock_adjustment_negative_disallowed(
    mock_db: MagicMock, mock_admin_token: TokenData
) -> None:
    # PATCH /adjust is ADMIN only; verify enterprise protection: cannot remove more than available
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 10,
                "reserved": 0,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_state)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": -11}  # available=10, removal=11 -> blocked
    response = client.patch("/api/v1/inventories/ALM-GHEE-250ML/adjust", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    # Enterprise protection: removal exceeds available quantity
    assert "Cannot remove" in response.json()["message"] or "would result in a negative stock level" in response.json()["message"]


@pytest.mark.anyio
async def test_stock_reservation_success(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 10,
                "reserved": 2,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return inventory_state

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        if "$set" in update_doc:
            inventory_state.update(update_doc["$set"])
        return inventory_state

    mock_db["inventories"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["inventories"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": 5}  # 10 - 2 = 8 available. 5 <= 8 is valid.
    response = client.post("/api/v1/inventories/ALM-GHEE-250ML/reserve", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["warehouse_stock"][0]["reserved"] == 7
    assert json_data["data"]["available_total"] == 3  # available is now 10 - 7 = 3


@pytest.mark.anyio
async def test_stock_reservation_over_reservation_prevention(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 10,
                "reserved": 2,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_state)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": 9}  # available = 8, 9 is invalid.
    response = client.post("/api/v1/inventories/ALM-GHEE-250ML/reserve", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "units are available" in response.json()["message"]


@pytest.mark.anyio
async def test_stock_release_success(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 10,
                "reserved": 5,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return inventory_state

    async def mock_find_one_and_update(
        filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any
    ) -> Any:
        if "$set" in update_doc:
            inventory_state.update(update_doc["$set"])
        return inventory_state

    mock_db["inventories"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["inventories"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": 3}  # release 3 from 5 reserved.
    response = client.post("/api/v1/inventories/ALM-GHEE-250ML/release", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["warehouse_stock"][0]["reserved"] == 2


@pytest.mark.anyio
async def test_stock_release_over_release_prevention(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    inventory_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "sku": "ALM-GHEE-250ML",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "warehouse_stock": [
            {
                "warehouse_id": "WH-MAIN",
                "on_hand": 10,
                "reserved": 5,
                "location_code": "A-1",
            }
        ],
        "safety_stock_level": 5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_state)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    payload = {"warehouse_id": "WH-MAIN", "quantity": 6}  # release 6 when only 5 reserved.
    response = client.post("/api/v1/inventories/ALM-GHEE-250ML/release", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "units are reserved" in response.json()["message"]


@pytest.mark.anyio
async def test_get_low_stock_alerts_query(
    mock_db: MagicMock, mock_warehouse_token: TokenData
) -> None:
    alerts_result = [
        {
            "_id": "60c72b2f9b1d8e2a3c4f5e6f",
            "sku": "ALM-GHEE-250ML",
            "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
            "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
            "warehouse_stock": [
                {
                    "warehouse_id": "WH-MAIN",
                    "on_hand": 5,
                    "reserved": 2,
                    "location_code": "A-1",
                }
            ],
            "safety_stock_level": 10,  # available = 3 < 10 safety level
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
    ]

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = alerts_result
    mock_db["inventories"].aggregate = AsyncMock(return_value=mock_cursor)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse_token

    response = client.get("/api/v1/inventories/alerts/low-stock")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["sku"] == "ALM-GHEE-250ML"
    assert json_data["data"][0]["is_low_stock"] is True
