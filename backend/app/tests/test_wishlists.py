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
        "wishlists": MagicMock(),
        "audit_logs": MagicMock(),
    }
    db.__getitem__.side_effect = lambda key: collections[key]
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
async def test_auth_required(mock_db: MagicMock) -> None:
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/wishlists/me")
    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert "Authorization headers missing" in response.json()["message"]


@pytest.mark.anyio
async def test_get_my_wishlist_lazy_create(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    mock_db["wishlists"].find_one = AsyncMock(return_value=None)
    mock_db["wishlists"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6f")
    )
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    response = client.get("/api/v1/wishlists/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["customer_id"] == "60c72b2f9b1d8e2a3c4f5e6e"
    assert json_data["data"]["items"] == []
    assert mock_db["wishlists"].insert_one.called


@pytest.mark.anyio
async def test_add_wishlist_item_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    # Stateful database simulation
    wishlist_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "items": [],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return wishlist_state

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            wishlist_state.update(update_doc["$set"])
        return wishlist_state

    mock_db["wishlists"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["wishlists"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
    }
    response = client.post("/api/v1/wishlists/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["items"]) == 1
    assert json_data["data"]["items"][0]["product_id"] == "60c72b2f9b1d8e2a3c4f5e6b"
    assert json_data["data"]["items"][0]["variant_id"] == "60c72b2f9b1d8e2a3c4f5e6c"
    assert json_data["data"]["items"][0]["product_summary"]["name"] == "Organic Almond Ghee"
    assert Decimal(str(json_data["data"]["items"][0]["product_summary"]["price"])) == Decimal("299.00")


@pytest.mark.anyio
async def test_add_wishlist_item_duplicate(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    wishlist_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "added_at": datetime.now(UTC),
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    mock_db["wishlists"].find_one = AsyncMock(return_value=wishlist_doc)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
    }
    response = client.post("/api/v1/wishlists/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already in your wishlist" in response.json()["message"]


@pytest.mark.anyio
async def test_add_wishlist_item_product_inactive_or_deleted(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    wishlist_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "items": [],
    }
    mock_db["wishlists"].find_one = AsyncMock(return_value=wishlist_doc)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b", status="draft")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
    }
    response = client.post("/api/v1/wishlists/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "does not exist, is inactive, or has been deleted" in response.json()["message"]


@pytest.mark.anyio
async def test_add_wishlist_item_limit_exceeded(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    items = [
        {
            "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
            "variant_id": f"var_{i}",
            "sku": f"SKU_{i}",
            "added_at": datetime.now(UTC),
        }
        for i in range(100)
    ]
    wishlist_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "items": items,
    }
    mock_db["wishlists"].find_one = AsyncMock(return_value=wishlist_doc)

    product_doc = create_mock_product_doc(
        "60c72b2f9b1d8e2a3c4f5e6b",
        variants=[
            {
                "variant_id": "new_var_id",
                "sku": "NEW-SKU",
                "title": "New Var",
                "volume_weight": "1L",
                "price": Decimal("399.00"),
                "compare_at_price": None,
                "stock_status": "in_stock",
                "is_active": True,
            }
        ],
    )
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    payload = {
        "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "variant_id": "new_var_id",
    }
    response = client.post("/api/v1/wishlists/me/items", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Wishlist limit reached" in response.json()["message"]


@pytest.mark.anyio
async def test_remove_wishlist_item_success(
    mock_db: MagicMock, mock_customer_token: TokenData
) -> None:
    # Stateful database simulation
    wishlist_state = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6f",
        "customer_id": "60c72b2f9b1d8e2a3c4f5e6e",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e6b",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-GHEE-250ML",
                "added_at": datetime.now(UTC),
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    async def mock_find_one(filter_query: Any, *args: Any, **kwargs: Any) -> Any:
        return wishlist_state

    async def mock_find_one_and_update(filter_query: Any, update_doc: Any, *args: Any, **kwargs: Any) -> Any:
        if "$set" in update_doc:
            wishlist_state.update(update_doc["$set"])
        return wishlist_state

    mock_db["wishlists"].find_one = AsyncMock(side_effect=mock_find_one)
    mock_db["wishlists"].find_one_and_update = AsyncMock(side_effect=mock_find_one_and_update)

    product_doc = create_mock_product_doc("60c72b2f9b1d8e2a3c4f5e6b")
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer_token

    response = client.delete("/api/v1/wishlists/me/items/60c72b2f9b1d8e2a3c4f5e6c")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["items"]) == 0
