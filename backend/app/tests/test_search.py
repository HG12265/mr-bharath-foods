import asyncio
from datetime import UTC, datetime
from decimal import Decimal
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
        "search_analytics": MagicMock(),
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


@pytest.mark.anyio
async def test_search_query_too_short(mock_db: MagicMock) -> None:
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/search?q=a")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "at least 2 characters" in response.json()["message"]


@pytest.mark.anyio
async def test_search_query_too_long(mock_db: MagicMock) -> None:
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/search?q=" + ("a" * 101))
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "cannot exceed 100 characters" in response.json()["message"]


@pytest.mark.anyio
async def test_search_products_success(mock_db: MagicMock) -> None:
    # 1. Mock Category Lookup for search word
    category_cursor = MagicMock()
    category_cursor.__aiter__.return_value = []
    mock_db["categories"].find = MagicMock(return_value=category_cursor)

    # 2. Mock Product Lookup
    product_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6b",
        "name": "Organic Almond Milk",
        "slug": "organic-almond-milk",
        "description": "Tasty organic almond milk.",
        "short_description": "Organic almond milk.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "media_ids": [],
        "sourcing": {"region": "California", "story": "Almond orchards."},
        "attributes": [],
        "variants": [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e6c",
                "sku": "ALM-MILK-1L",
                "title": "1 Liter",
                "volume_weight": "1L",
                "price": Decimal("199.00"),
                "stock_status": "in_stock",
                "is_active": True,
            }
        ],
        "seo": {"meta_title": None, "meta_description": None, "meta_keywords": []},
        "ratings": {"average_rating": 4.5, "review_count": 10},
        "tags": ["organic", "almond", "milk"],
        "search_keywords": ["almond milk", "nut milk"],
        "is_featured": True,
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    product_cursor = MagicMock()
    product_cursor.sort.return_value = product_cursor
    product_cursor.skip.return_value = product_cursor
    product_cursor.limit.return_value = product_cursor
    product_cursor.__aiter__.return_value = [product_doc]
    mock_db["products"].find = MagicMock(return_value=product_cursor)

    # Mock count_documents
    mock_db["products"].count_documents = AsyncMock(return_value=1)

    # Mock search analytics log insertion
    mock_db["search_analytics"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="60c72b2f9b1d8e2a3c4f5e6d"))

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/search?q=almond")
    app.dependency_overrides.clear()

    # Yield control to the event loop so background logging task can execute
    await asyncio.sleep(0.05)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "Organic Almond Milk"
    assert json_data["meta"]["total_docs"] == 1
    assert mock_db["search_analytics"].insert_one.called


@pytest.mark.anyio
async def test_search_categories_success(mock_db: MagicMock) -> None:
    category_doc = {
        "_id": "60c72b2f9b1d8e2a3c4f5e6a",
        "name": "Dairy Alternatives",
        "slug": "dairy-alternatives",
        "description": "Non-dairy milk alternatives.",
        "image_id": None,
        "parent_id": None,
        "level": 0,
        "sort_order": 2,
        "is_active": True,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    category_cursor = MagicMock()
    category_cursor.skip.return_value = category_cursor
    category_cursor.limit.return_value = category_cursor
    category_cursor.__aiter__.return_value = [category_doc]
    mock_db["categories"].find = MagicMock(return_value=category_cursor)
    mock_db["categories"].count_documents = AsyncMock(return_value=1)
    mock_db["search_analytics"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/search?q=dairy&type=category")
    app.dependency_overrides.clear()

    # Yield control to the event loop so background logging task can execute
    await asyncio.sleep(0.05)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "Dairy Alternatives"
    assert json_data["meta"]["total_docs"] == 1


@pytest.mark.anyio
async def test_autocomplete_endpoint(mock_db: MagicMock) -> None:
    # 1. Product Mock
    prod_doc = {
        "name": "Raw Honey",
        "tags": ["sweetener", "natural honey"],
        "search_keywords": ["raw sweet honey"],
    }
    product_cursor = MagicMock()
    product_cursor.limit.return_value = product_cursor
    product_cursor.__aiter__.return_value = [prod_doc]
    mock_db["products"].find = MagicMock(return_value=product_cursor)

    # 2. Category Mock
    cat_doc = {
        "name": "Honey Spreads",
    }
    category_cursor = MagicMock()
    category_cursor.limit.return_value = category_cursor
    category_cursor.__aiter__.return_value = [cat_doc]
    mock_db["categories"].find = MagicMock(return_value=category_cursor)

    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/search/autocomplete?q=hone")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    suggestions = json_data["data"]["suggestions"]
    assert "Raw Honey" in suggestions
    assert "Honey Spreads" in suggestions
    # Sweetener shouldn't match "hone" prefix
    assert "sweetener" not in suggestions


@pytest.mark.anyio
async def test_trending_searches_endpoint(mock_db: MagicMock) -> None:
    agg_result = [
        {"query": "organic ghee", "count": 25},
        {"query": "honey", "count": 14},
    ]
    cursor = MagicMock()
    cursor.__aiter__.return_value = agg_result
    mock_db["search_analytics"].aggregate = AsyncMock(return_value=cursor)

    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/search/trending")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    trending = json_data["data"]["trending"]
    assert len(trending) == 2
    assert trending[0]["query"] == "organic ghee"
    assert trending[0]["count"] == 25
