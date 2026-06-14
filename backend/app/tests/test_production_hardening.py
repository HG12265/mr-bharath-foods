from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.core.startup_checks import run_startup_checks
from app.schemas.auth import TokenData
from main import app

client = TestClient(app)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    collections = {}

    def get_mock_collection(key: str) -> MagicMock:
        if key not in collections:
            coll = MagicMock()
            coll.insert_one = AsyncMock()
            coll.find_one = AsyncMock(return_value=None)
            coll.find_one_and_update = AsyncMock(return_value=None)
            coll.update_many = AsyncMock()
            coll.update_one = AsyncMock()
            coll.count_documents = AsyncMock(return_value=0)
            coll.aggregate = MagicMock()
            coll.create_index = AsyncMock()
            collections[key] = coll
        return collections[key]

    db.__getitem__.side_effect = get_mock_collection
    return db


# --- 1. Startup Index Registry Tests ---

@pytest.mark.anyio
async def test_initialize_indexes(mock_db: MagicMock) -> None:
    from app.core.index_registry import initialize_indexes
    await initialize_indexes(mock_db)

    # Check that create_index was called for reviews with the partialFilterExpression
    mock_db["reviews"].create_index.assert_any_call(
        [("product_id", 1), ("customer_id", 1)],
        unique=True,
        partialFilterExpression={"is_deleted": {"$eq": False}}
    )
    # Check that create_index was called for other collections
    mock_db["customers"].create_index.assert_any_call([("auth.email", 1)], unique=True, sparse=True)
    mock_db["inventories"].create_index.assert_any_call([("sku", 1)], unique=True)


# --- 2. Global Health Readiness Check Tests ---

@pytest.mark.anyio
async def test_readiness_probe_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock db_manager and redis_manager to be connected
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(return_value={"ok": 1.0})

    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock(return_value=True)

    from app.core.database import db_manager
    from app.core.redis import redis_manager

    monkeypatch.setattr(db_manager, "client", mock_client)
    monkeypatch.setattr(redis_manager, "client", mock_redis)

    response = client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["database"] == "healthy"
    assert res_data["data"]["redis"] == "healthy"

    # Check new path
    response_new = client.get("/api/v1/readiness")
    assert response_new.status_code == 200
    res_data_new = response_new.json()
    assert res_data_new["success"] is True
    assert res_data_new["data"]["database"] == "healthy"
    assert res_data_new["data"]["redis"] == "healthy"


@pytest.mark.anyio
async def test_readiness_probe_unhealthy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock db_manager to raise an exception on ping
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(side_effect=Exception("DB Down"))

    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock(return_value=True)

    from app.core.database import db_manager
    from app.core.redis import redis_manager

    monkeypatch.setattr(db_manager, "client", mock_client)
    monkeypatch.setattr(redis_manager, "client", mock_redis)

    response = client.get("/api/v1/health/readiness")
    assert response.status_code == 503
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["data"]["database"] == "unhealthy"
    assert res_data["data"]["redis"] == "healthy"

    # Check new path
    response_new = client.get("/api/v1/readiness")
    assert response_new.status_code == 503
    res_data_new = response_new.json()
    assert res_data_new["success"] is False
    assert res_data_new["data"]["database"] == "unhealthy"
    assert res_data_new["data"]["redis"] == "healthy"


# --- 3. Security Config Verification & Admin Production Checklist Tests ---

@pytest.mark.anyio
async def test_startup_checks_and_admin_checklist(mock_db: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.database import db_manager

    # Configure defaults in settings to test warnings
    monkeypatch.setattr(settings, "SECRET_KEY", "generate_a_secure_random_string_signature")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    checks = run_startup_checks()
    assert checks["secret_key"]["pass"] is False

    # Mock admin current user
    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@bharathdelight.in",
        role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    # Mock settings repo check
    mock_db["settings"].find_one = AsyncMock(
        return_value={
            "_id": ObjectId(),
            "upi_id": "test@upi",
            "tax_percentage": Decimal("5.00"),
            "shipping_fee": Decimal("50.00"),
            "free_shipping_threshold": Decimal("500.00"),
            "support_contact": "support@bharathdelight.in",
            "fssai_number": "12345678901234",
            "gst_number": "33AABCM1234D1Z5",
            "is_deleted": False,
        }
    )

    # Connect client & db_manager mock
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(return_value={"ok": 1.0})
    monkeypatch.setattr(db_manager, "client", mock_client)

    response = client.get("/api/v1/admin/production-checklist")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert "checklist" in res_data["data"]
    assert res_data["data"]["checklist"]["secret_key"]["pass"] is False
    assert res_data["data"]["checklist"]["settings_initialized"]["pass"] is True


# --- 4. Request Size Limits Middleware Tests ---

@pytest.mark.anyio
async def test_request_size_limit_middleware() -> None:
    from fastapi import FastAPI

    from app.middleware.request_size import RequestSizeLimitMiddleware

    test_app = FastAPI()
    test_app.add_middleware(RequestSizeLimitMiddleware, max_size_bytes=100)

    @test_app.post("/test")
    def test_route() -> dict[str, bool]:
        return {"ok": True}

    test_client = TestClient(test_app)

    # 1. Send large body -> should be rejected with 413
    payload = "A" * 200
    response = test_client.post("/test", content=payload)
    assert response.status_code == 413
    assert "payload size exceeds the limit" in response.json()["message"]

    # 2. Send small body -> should pass through
    response_ok = test_client.post("/test", content="small payload")
    assert response_ok.status_code == 200


# --- 5. Global Pagination Limits Capping Tests ---

@pytest.mark.anyio
async def test_global_pagination_limits_cap(mock_db: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "MAX_PAGINATION_LIMIT", 5)

    from pydantic import BaseModel

    from app.repositories.base import BaseRepository

    class DummyModel(BaseModel):
        name: str

    repo = BaseRepository[DummyModel](mock_db, "dummy", DummyModel)

    # Mock collection find cursor
    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)

    # Define an async generator mock for cursor
    async def async_generator() -> Any:
        yield {"_id": ObjectId(), "name": "item1"}
        yield {"_id": ObjectId(), "name": "item2"}

    mock_cursor.__aiter__ = lambda self: async_generator()
    mock_db["dummy"].find = MagicMock(return_value=mock_cursor)

    await repo.find({}, limit=1000)

    # Assert limit was capped to 5
    mock_cursor.limit.assert_called_with(5)


# --- 6. API Version Response Header & GET / Metadata Endpoint Tests ---

@pytest.mark.anyio
async def test_api_version_header_and_root_metadata() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-API-Version") == settings.PROJECT_VERSION
    assert response.json()["version"] == settings.PROJECT_VERSION
    assert response.json()["status"] == "running"


# --- 7. Production Hardening: Auth & Media Resolution Tests ---

@pytest.mark.anyio
async def test_auth_me_anonymous_returns_401(mock_db: MagicMock) -> None:
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/auth/me")
    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.anyio
async def test_product_media_resolution(mock_db: MagicMock) -> None:
    from app.models.product import Product
    from app.repositories.product_repository import ProductRepository
    from app.repositories.media_repository import MediaRepository
    from app.api.v1.products import map_product_response

    # Mock product document
    product_doc = {
        "_id": ObjectId("6a2d1180f8d9ad332876e900"),
        "name": "Test Ghee",
        "slug": "test-ghee",
        "description": "Premium Ghee",
        "short_description": "Premium",
        "category_id": "cat_123",
        "media_ids": ["6a2d1180f8d9ad332876e91b", "invalid_id_as_url_or_something"],
        "sourcing": {"region": "Tamil Nadu", "story": "Made with love", "manufacturer_id": "mfg_123"},
        "attributes": [],
        "variants": [],
        "seo": {"meta_title": "Ghee", "meta_description": "Ghee desc", "meta_keywords": []},
        "ratings": {"average_rating": 4.5, "review_count": 10, "total_reviews": 10},
        "tags": [],
        "search_keywords": [],
        "is_featured": True,
        "status": "active",
        "is_deleted": False,
        "created_at": "2026-06-14T08:00:00Z",
        "updated_at": "2026-06-14T08:00:00Z"
    }

    # Mock media asset document
    media_doc = {
        "_id": ObjectId("6a2d1180f8d9ad332876e91b"),
        "original_filename": "rasipuram-ghee.jpg",
        "content_type": "image/jpeg",
        "size": 100,
        "storage_key": "media/product_image/admin/6a2d1180f8d9ad332876e91b-rasipuram-ghee.jpg",
        "public_url": "https://res.cloudinary.com/test/rasipuram-ghee.jpg",
        "uploaded_by": "admin",
        "asset_type": "product_image",
        "status": "completed",
        "is_deleted": False,
        "created_at": "2026-06-14T08:00:00Z",
        "updated_at": "2026-06-14T08:00:00Z"
    }

    # Mock DB collections for repo lookups
    # Product lookup
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    # Media asset lookup
    # Find cursor mock for media_repo.collection.find
    mock_cursor = MagicMock()
    async def async_generator() -> Any:
        yield media_doc
    mock_cursor.__aiter__ = lambda self: async_generator()
    mock_db["media_assets"].find = MagicMock(return_value=mock_cursor)

    product_repo = ProductRepository(mock_db)
    media_repo = MediaRepository(mock_db)

    # Fetch product via repo
    product = await product_repo.get_by_id("6a2d1180f8d9ad332876e900")
    assert product is not None

    # Call map_product_response to map the db product to response schema
    response_data = await map_product_response(product, media_repo)

    # Check media_ids are mapped to resolved public_urls
    assert len(response_data.media_ids) == 2
    assert response_data.media_ids[0] == "https://res.cloudinary.com/test/rasipuram-ghee.jpg"
    assert response_data.media_ids[1] == "invalid_id_as_url_or_something"


@pytest.mark.anyio
async def test_query_non_existent_media_returns_404(mock_db: MagicMock) -> None:
    # Query returns None for non-existent media asset
    mock_db["media_assets"].find_one = AsyncMock(return_value=None)
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/v1/media/6a2d1180f8d9ad332876e000")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json()["success"] is False
