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
    collections = {
        "products": MagicMock(),
        "categories": MagicMock(),
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


@pytest.fixture  # type: ignore[untyped-decorator]
def mock_admin_token_data() -> TokenData:
    return TokenData(
        user_id="admin_user_id_12345",
        email="admin@bharathdelight.in",
        role=UserRole.ADMIN
    )


def test_create_product_success(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    # 1. Mock Category Lookup (Category must exist, be active, not deleted)
    category_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "name": "Organic Ghee",
        "slug": "organic-ghee",
        "is_active": True,
        "is_deleted": False,
        "level": 0
    }
    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)

    # 2. Mock Media Assets (Media must exist, not deleted, and be completed)
    media_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "original_filename": "image.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/uuid-image.png",
        "public_url": "https://r2.com/image.png",
        "status": "completed",
        "is_deleted": False,
        "uploaded_by": "admin_user_id_12345",
        "asset_type": "product"
    }
    mock_db["media_assets"].find_one = AsyncMock(return_value=media_doc)

    # 3. Mock Slug & SKU Uniqueness (No duplicate slug or SKU in DB)
    mock_db["products"].find_one = AsyncMock(return_value=None)
    mock_db["products"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e7c"))
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    payload = {
        "name": "Premium Cow Ghee",
        "description": "Premium quality organic cow ghee directly sourced from local farms.",
        "short_description": "Pure premium organic cow ghee.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "media_ids": ["60c72b2f9b1d8e2a3c4f5e7b"],
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

    assert response.status_code == 200, response.json()
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Premium Cow Ghee"
    assert json_data["data"]["variants"][0]["sku"] == "COW-GHEE-500ML"


def test_create_product_duplicate_sku(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    # Category exists and active
    category_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "name": "Organic Ghee",
        "slug": "organic-ghee",
        "is_active": True,
        "is_deleted": False,
        "level": 0
    }
    # Mock category find_one, and mock media lookup
    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)

    media_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "original_filename": "image.png",
        "content_type": "image/png",
        "size": 1024,
        "storage_key": "media/avatar/uuid-image.png",
        "public_url": "https://r2.com/image.png",
        "status": "completed",
        "is_deleted": False,
        "uploaded_by": "admin_user_id_12345",
        "asset_type": "product"
    }
    mock_db["media_assets"].find_one = AsyncMock(return_value=media_doc)

    # Return an existing product for the SKU check (meaning duplicate)
    existing_product_with_sku = {
        "_id": "60c72b2f9b1d8e2a3c4f5e7c",
        "name": "Different Ghee Product",
        "slug": "different-ghee",
        "description": "Decent description of different ghee that is long enough.",
        "short_description": "Pure organic different ghee.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "variants": [],
        "sourcing": {
            "region": "West Bengal",
            "story": "Sourced from native cows."
        },
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
        "category_id": "60c72b2f9b1d8e2a3c4f5e7a",
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
        "_id": "60c72b2f9b1d8e2a3c4f5e7c",
        "name": "Active Cow Ghee",
        "slug": "active-cow-ghee",
        "description": "Standard ghee description.",
        "short_description": "Short ghee description.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "media_ids": [],
        "sourcing": {"region": "Tami Nadu", "story": "Grass-fed cows."},
        "attributes": [],
        "variants": [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e7b",
                "sku": "COW-GHEE-500ML",
                "title": "500ml",
                "volume_weight": "500ml",
                "price": Decimal("499.00"),
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
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
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
