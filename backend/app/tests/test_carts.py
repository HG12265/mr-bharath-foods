from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
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
def mock_customer_token() -> TokenData:
    return TokenData(
        user_id="60c72b2f9b1d8e2a3c4f5e6e",
        email="customer@mrbharathfoods.in",
        role=UserRole.CUSTOMER,
    )


def create_mock_product_doc(
    product_id: str,
    status: str = "active",
    is_deleted: bool = False,
    variants: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if variants is None:
        variants = [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "title": "250ml",
                "volume_weight": "250ml",
                "price": Decimal("299.00"),
                "compare_at_price": None,
                "stock_status": "in_stock",
                "is_active": True,
            }
        ]
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
        "variants": variants,
        "seo": {"meta_title": None, "meta_description": None, "meta_keywords": []},
        "ratings": {"average_rating": 4.5, "review_count": 5},
        "status": status,
        "is_deleted": is_deleted,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.mark.anyio
async def test_get_my_cart_logged_in_lazy_create(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    mock_db["carts"].find_one = AsyncMock(return_value=None)
    mock_db["carts"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6f")
    )
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    response = client.get("/api/v1/carts/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["customer_id"] == mock_customer_token.user_id
    assert json_data["data"]["items"] == []
    assert json_data["data"]["summary"]["subtotal"] == "0.00"
    assert json_data["data"]["summary"]["item_count"] == 0
    assert json_data["data"]["summary"]["quantity_total"] == 0
    assert mock_db["carts"].insert_one.called


@pytest.mark.anyio
async def test_get_my_cart_guest_generate_token(mock_db: MagicMock) -> None:
    mock_db["carts"].find_one = AsyncMock(return_value=None)
    mock_db["carts"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6f")
    )
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: None

    response = client.get("/api/v1/carts/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    guest_token = json_data["data"]["guest_token"]
    assert guest_token is not None
    assert response.headers.get("X-Guest-Token") == guest_token
    assert json_data["data"]["customer_id"] is None
    assert mock_db["carts"].insert_one.called


@pytest.mark.anyio
async def test_get_my_cart_guest_reuse_token(mock_db: MagicMock) -> None:
    test_token = "44444444-4444-4444-4444-444444444444"
    cart_doc: dict[str, Any] = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": None,
        "guest_token": test_token,
        "items": [],
        "status": "active",
        "expires_at": datetime.now(UTC),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: None

    response = client.get("/api/v1/carts/me", headers={"X-Guest-Token": test_token})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["guest_token"] == test_token
    assert response.headers.get("X-Guest-Token") == test_token


@pytest.mark.anyio
async def test_add_cart_item_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        if "customer_id" in filter_query or "_id" in filter_query:
            return cart_state
        return None

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            cart_state.update(update_doc["$set"])
        return cart_state

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "quantity": 2,
    }
    response = client.post("/api/v1/carts/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["items"]) == 1
    assert json_data["data"]["items"][0]["quantity"] == 2
    assert json_data["data"]["items"][0]["sku"] == "ALM-GHEE-250ML"
    assert Decimal(str(json_data["data"]["summary"]["subtotal"])) == Decimal("598.00")
    assert json_data["data"]["summary"]["quantity_total"] == 2


@pytest.mark.anyio
async def test_add_cart_item_duplicate_caps_quantity(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 8,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        if "customer_id" in filter_query or "_id" in filter_query:
            return cart_state
        return None

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            cart_state.update(update_doc["$set"])
        return cart_state

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
        "quantity": 5,  # 8 + 5 = 13, should be capped at 10
    }
    response = client.post("/api/v1/carts/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["items"][0]["quantity"] == 10
    assert Decimal(str(json_data["data"]["summary"]["subtotal"])) == Decimal("2990.00")


@pytest.mark.anyio
async def test_update_cart_item_quantity_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return cart_state

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            cart_state.update(update_doc["$set"])
        return cart_state

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    response = client.patch(
        "/api/v1/carts/me/items/60c72b2f9b1d8e2a3c4f5e6c", json={"quantity": 5}
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["items"][0]["quantity"] == 5
    assert Decimal(str(json_data["data"]["summary"]["subtotal"])) == Decimal("1495.00")


@pytest.mark.anyio
async def test_update_cart_item_quantity_exceeds_limits(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    mock_db["carts"].find_one = AsyncMock(return_value=cart_state)
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    response = client.patch(
        "/api/v1/carts/me/items/60c72b2f9b1d8e2a3c4f5e6c", json={"quantity": 11}
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "cannot exceed 10" in response.json()["message"]


@pytest.mark.anyio
async def test_remove_cart_item_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return cart_state

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            cart_state.update(update_doc["$set"])
        return cart_state

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    response = client.delete("/api/v1/carts/me/items/60c72b2f9b1d8e2a3c4f5e6c")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["items"] == []


@pytest.mark.anyio
async def test_clear_cart_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 2,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return cart_state

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            cart_state.update(update_doc["$set"])
        return cart_state

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_customer_token

    response = client.delete("/api/v1/carts/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["items"] == []


@pytest.mark.anyio
async def test_merge_carts_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    guest_token = "55555555-5555-5555-5555-555555555555"

    customer_cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": mock_customer_token.user_id,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 3,
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    guest_cart_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "customer_id": None,
        "guest_token": guest_token,
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "quantity": 5,  # duplicate variant: 3 + 5 = 8
                "unit_price_snapshot": Decimal("299.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e67",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e68",
                "sku": "HONEY-1KG",
                "quantity": 2,  # new item
                "unit_price_snapshot": Decimal("599.00"),
                "added_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        ],
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        if filter_query.get("customer_id") == mock_customer_token.user_id:
            return customer_cart_state
        if filter_query.get("guest_token") == guest_token:
            return guest_cart_state
        return None

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        target_id = str(filter_query.get("_id")) if filter_query.get("_id") else None
        if target_id == customer_cart_state["_id"] or filter_query.get("customer_id") == mock_customer_token.user_id:
            if "$set" in update_doc:
                customer_cart_state.update(update_doc["$set"])
            return customer_cart_state
        if target_id == guest_cart_state["_id"] or filter_query.get("guest_token") == guest_token:
            if "$set" in update_doc:
                guest_cart_state.update(update_doc["$set"])
            return guest_cart_state
        return None

    mock_db["carts"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["carts"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    # Mock products lookup
    product1_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    product2_doc = create_mock_product_doc(
        "60c72b2f9b1d8e2a3c4f5e67",
        variants=[
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e68",
                "sku": "HONEY-1KG",
                "title": "1kg",
                "volume_weight": "1kg",
                "price": Decimal("599.00"),
                "compare_at_price": None,
                "stock_status": "in_stock",
                "is_active": True,
            }
        ],
    )

    async def mock_product_find_by_id(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        product_id = str(filter_query.get("_id")) if filter_query.get("_id") else ""
        if product_id == "60c72b2f9b1d8e2a3c4f5e6b":
            return product1_doc
        if product_id == "60c72b2f9b1d8e2a3c4f5e67":
            return product2_doc
        return None

    mock_db["products"].find_one = AsyncMock(side_effect=mock_product_find_by_id)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Require Customer Role for merge
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    response = client.post("/api/v1/carts/merge", json={"guest_token": guest_token})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["customer_id"] == mock_customer_token.user_id
    assert len(json_data["data"]["items"]) == 2

    # Verify duplicate variant got incremented
    item1 = next(item for item in json_data["data"]["items"] if item["variant_id"] == "60c72b2f9b1d8e2a3c4f5e6c")
    assert item1["quantity"] == 8

    # Verify new item got added
    item2 = next(item for item in json_data["data"]["items"] if item["variant_id"] == "60c72b2f9b1d8e2a3c4f5e68")
    assert item2["quantity"] == 2

    # Verify guest cart is marked converted
    assert guest_cart_state["status"] == "converted"
