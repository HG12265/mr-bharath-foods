from datetime import UTC, datetime
from decimal import Decimal
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
    db["products"] = MagicMock()
    db["categories"] = MagicMock()
    db["media_assets"] = MagicMock()
    db["audit_logs"] = MagicMock()
    return db


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_admin_token_data() -> TokenData:
    return TokenData(
        user_id="admin_user_id_12345",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )


def test_create_product_success(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    # 1. Mock Category Lookup (Category must exist, be active, not deleted)
    category_doc = {
        "_id": "category_id_123",
        "name": "Organic Ghee",
        "slug": "organic-ghee",
        "is_active": True,
        "is_deleted": False,
        "level": 0
    }
    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)

    # 2. Mock Media Assets (Media must exist, not deleted, and be completed)
    media_doc = {
        "_id": "media_id_456",
        "status": "completed",
        "is_deleted": False,
        "uploaded_by": "admin_user_id_12345"
    }
    mock_db["media_assets"].find_one = AsyncMock(return_value=media_doc)

    # 3. Mock Slug & SKU Uniqueness (No duplicate slug or SKU in DB)
    mock_db["products"].find_one = AsyncMock(return_value=None)
    mock_db["products"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="prod_id_789"))
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    payload = {
        "name": "Premium Cow Ghee",
        "description": "Premium quality organic cow ghee directly sourced from local farms.",
        "short_description": "Pure premium organic cow ghee.",
        "category_id": "category_id_123",
        "media_ids": ["media_id_456"],
        "sourcing": {
            "region": "Tamil Nadu",
            "story": "Sourced from native cows in clean pastures of Western Ghats."
        },
        "attributes": [
            {"name": "Organic", "value": "Yes"},
            {"name": "Preservatives", "value": "None"}
        ],
        "variants": [
            {
                "sku": "COW-GHEE-500ML",
                "title": "500ml Glass Jar",
                "volume_weight": "500ml",
                "price": "499.00",
                "compare_at_price": "550.00",
                "stock_status": "in_stock",
                "is_active": True
            }
        ],
        "seo": {
            "meta_title": "Buy Premium Cow Ghee Online",
            "meta_description": "Pure organic cow ghee.",
            "meta_keywords": ["ghee", "cow ghee", "organic"]
        },
        "status": "active"
    }

    response = client.post("/api/v1/products", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Premium Cow Ghee"
    assert json_data["data"]["variants"][0]["sku"] == "COW-GHEE-500ML"


def test_create_product_duplicate_sku(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    # Category exists and active
    category_doc = {"_id": "cat_id", "is_active": True, "is_deleted": False}
    # Mock category find_one, and mock media lookup
    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)
    mock_db["media_assets"].find_one = AsyncMock(return_value={"_id": "m_id", "status": "completed", "is_deleted": False})

    # Return an existing product for the SKU check (meaning duplicate)
    existing_product_with_sku = {
        "_id": "another_prod_id",
        "name": "Different Ghee Product",
        "slug": "different-ghee",
        "is_deleted": False
    }
    # First slug lookup returns None (slug unique), next SKU lookup returns existing product
    mock_db["products"].find_one = AsyncMock(side_effect=[None, existing_product_with_sku])

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    payload = {
        "name": "Cow Ghee",
        "description": "Decent description of cow ghee that is long enough.",
        "short_description": "Pure organic cow ghee.",
        "category_id": "cat_id",
        "variants": [
            {
                "sku": "COW-GHEE-500ML",
                "title": "500ml Jar",
                "volume_weight": "500ml",
                "price": "450.00"
            }
        ],
        "sourcing": {
            "region": "West Bengal",
            "story": "Sourced from native cows."
        }
    }

    response = client.post("/api/v1/products", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already in use" in response.json()["message"]


def test_public_list_visibility(
    mock_db: MagicMock
) -> None:
    # Public listing should query status="active" and is_deleted!=True
    product_doc = {
        "_id": "active_prod_id",
        "name": "Active Cow Ghee",
        "slug": "active-cow-ghee",
        "description": "Standard ghee description.",
        "short_description": "Short ghee description.",
        "category_id": "cat_id",
        "media_ids": [],
        "sourcing": {"region": "Tami Nadu", "story": "Grass-fed cows."},
        "attributes": [],
        "variants": [
            {
                "variant_id": "v_id",
                "sku": "COW-GHEE-500ML",
                "title": "500ml",
                "volume_weight": "500ml",
                "price": Decimal("499.00"),
                "compare_at_price": None,
                "stock_status": "in_stock",
                "is_active": True
            }
        ],
        "seo": {"meta_title": None, "meta_description": None, "meta_keywords": []},
        "ratings": {"average_rating": 0.0, "review_count": 0},
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = [product_doc]
    mock_db["products"].find = MagicMock(return_value=mock_cursor)

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/products")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "Active Cow Ghee"
