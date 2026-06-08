from datetime import UTC, datetime
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
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )


def test_create_category_duplicate_slug(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    # Set up mocks: check get_by_slug returns existing category (meaning duplicate)
    existing_cat = {
        "_id": "507f1f77bcf86cd799439111",
        "name": "Old Category",
        "slug": "duplicate-slug",
        "level": 0,
        "is_active": True,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["categories"].find_one = AsyncMock(return_value=existing_cat)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    payload = {
        "name": "New Category",
        "slug": "duplicate-slug",
        "is_active": True
    }

    response = client.post("/api/v1/categories", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already in use" in response.json()["message"]


def test_circular_dependency_parent_itself(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    category_doc = {
        "_id": "507f1f77bcf86cd799439111",
        "name": "Loop Category",
        "slug": "loop-cat",
        "level": 0,
        "is_active": True,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    # Attempt to set parent to itself
    payload = {
        "parent_id": "507f1f77bcf86cd799439111"
    }

    response = client.patch("/api/v1/categories/507f1f77bcf86cd799439111", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "own parent" in response.json()["message"]


def test_tree_generation(
    mock_db: MagicMock
) -> None:
    # Set up flat categories:
    # Ghee (id: root_id, parent_id: None)
    # Cow Ghee (id: cow_id, parent_id: root_id)
    # Buffalo Ghee (id: buffalo_id, parent_id: root_id)
    categories = [
        {
            "_id": "root_id",
            "name": "Ghee",
            "slug": "ghee",
            "description": None,
            "image_id": None,
            "parent_id": None,
            "level": 0,
            "sort_order": 1,
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        },
        {
            "_id": "cow_id",
            "name": "Cow Ghee",
            "slug": "cow-ghee",
            "description": None,
            "image_id": None,
            "parent_id": "root_id",
            "level": 1,
            "sort_order": 1,
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        },
        {
            "_id": "buffalo_id",
            "name": "Buffalo Ghee",
            "slug": "buffalo-ghee",
            "description": None,
            "image_id": None,
            "parent_id": "root_id",
            "level": 1,
            "sort_order": 2,
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        },
    ]

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = categories
    mock_db["categories"].find = MagicMock(return_value=mock_cursor)

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/categories/tree")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True

    # Assert hierarchy
    tree_data = json_data["data"]
    assert len(tree_data) == 1  # 1 root node (Ghee)
    root_node = tree_data[0]
    assert root_node["name"] == "Ghee"
    assert len(root_node["children"]) == 2
    assert root_node["children"][0]["name"] == "Cow Ghee"
    assert root_node["children"][1]["name"] == "Buffalo Ghee"


def test_update_category_clear_fields(
    mock_db: MagicMock,
    mock_admin_token_data: TokenData
) -> None:
    category_doc = {
        "_id": "507f1f77bcf86cd799439111",
        "name": "Test Category",
        "slug": "test-cat",
        "description": "Some description",
        "image_id": "507f1f77bcf86cd799439222",
        "parent_id": "507f1f77bcf86cd799439333",
        "level": 1,
        "is_active": True,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["categories"].find_one = AsyncMock(return_value=category_doc)

    updated_doc = {
        **category_doc,
        "description": None,
        "image_id": None,
        "parent_id": None,
        "level": 0
    }
    mock_db["categories"].find_one_and_update = AsyncMock(return_value=updated_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin_token_data

    payload = {
        "description": None,
        "image_id": None,
        "parent_id": None
    }

    response = client.patch("/api/v1/categories/507f1f77bcf86cd799439111", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["description"] is None
    assert json_data["data"]["image_id"] is None
    assert json_data["data"]["parent_id"] is None
    assert json_data["data"]["level"] == 0

    # Verify that find_one_and_update was called with the cleared fields set to None
    called_args = mock_db["categories"].find_one_and_update.call_args[0]
    called_kwargs = mock_db["categories"].find_one_and_update.call_args[1]

    update_op = called_args[1] if len(called_args) > 1 else called_kwargs.get("update")
    assert update_op is not None
    assert "$set" in update_op
    assert update_op["$set"]["description"] is None
    assert update_op["$set"]["image_id"] is None
    assert update_op["$set"]["parent_id"] is None

