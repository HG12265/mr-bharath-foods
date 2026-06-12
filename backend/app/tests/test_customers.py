from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db, get_redis
from app.core.roles import UserRole
from app.schemas.auth import TokenData
from main import app

client = TestClient(app)

@pytest.fixture  # type: ignore[untyped-decorator]
def mock_db() -> MagicMock:
    db = MagicMock()
    collections = {
        "customers": MagicMock(),
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
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis

@pytest.fixture  # type: ignore[untyped-decorator]
def mock_token_data() -> TokenData:
    return TokenData(
        user_id="507f1f77bcf86cd799439011",
        email="test@bharathdelight.in",
        role=UserRole.CUSTOMER
    )

def test_get_customer_profile(mock_db: MagicMock, mock_token_data: TokenData) -> None:
    customer_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "auth": {
            "email": "test@bharathdelight.in",
            "phone": "+919876543210",
            "status": "active",
            "role": "customer"
        },
        "personal_details": {
            "first_name": "Gowtham",
            "last_name": "Kumar"
        },
        "addresses": [],
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["customers"].find_one = AsyncMock(return_value=customer_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    response = client.get("/api/v1/customers/me")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["personal_details"]["first_name"] == "Gowtham"

def test_add_customer_address(mock_db: MagicMock, mock_token_data: TokenData) -> None:
    customer_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "auth": {
            "email": "test@bharathdelight.in",
            "phone": "+919876543210",
            "status": "active",
            "role": "customer"
        },
        "personal_details": {
            "first_name": "Gowtham",
            "last_name": "Kumar"
        },
        "addresses": [],
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["customers"].find_one = AsyncMock(return_value=customer_doc)
    mock_db["customers"].find_one_and_update = AsyncMock(return_value=customer_doc)
    mock_db["audit_logs"].insert_one = AsyncMock(return_value=MagicMock())

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    payload = {
        "name": "Home Address",
        "phone": "+919876543210",
        "street": "123 Saffron Street",
        "landmark": "Near Temple",
        "pincode": "600001",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "is_default_shipping": True,
        "is_default_billing": True
    }

    response = client.post("/api/v1/customers/me/addresses", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True

def test_deactivate_profile(mock_db: MagicMock, mock_redis: AsyncMock, mock_token_data: TokenData) -> None:
    mock_db["customers"].update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_db["audit_logs"].insert_one = AsyncMock(return_value=MagicMock())

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    headers = {"Authorization": "Bearer fake_token_claims"}
    response = client.delete("/api/v1/customers/me", headers=headers)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "deactivated" in json_data["message"]


def test_update_profile_and_address_clear_nullable(mock_db: MagicMock, mock_token_data: TokenData) -> None:
    customer_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "auth": {
            "email": "test@bharathdelight.in",
            "phone": "+919876543210",
            "status": "active",
            "role": "customer"
        },
        "personal_details": {
            "first_name": "Gowtham",
            "last_name": "Kumar",
            "avatar_url": "https://avatar.png"
        },
        "addresses": [
            {
                "address_id": "addr-111",
                "name": "Home Address",
                "phone": "+919876543210",
                "street": "123 Saffron Street",
                "landmark": "Near Temple",
                "pincode": "600001",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "is_default_shipping": True,
                "is_default_billing": True
            }
        ],
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    mock_db["customers"].find_one = AsyncMock(return_value=customer_doc)
    mock_db["customers"].find_one_and_update = AsyncMock(return_value=customer_doc)
    mock_db["audit_logs"].insert_one = AsyncMock(return_value=MagicMock())

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_token_data

    # 1. Update profile - set avatar_url to null
    payload_profile = {
        "avatar_url": None
    }
    response_profile = client.patch("/api/v1/customers/me", json=payload_profile)
    assert response_profile.status_code == 200

    called_args = mock_db["customers"].find_one_and_update.call_args[0]
    called_kwargs = mock_db["customers"].find_one_and_update.call_args[1]
    update_op = called_args[1] if len(called_args) > 1 else called_kwargs.get("update")
    assert update_op["$set"]["personal_details.avatar_url"] is None

    # Reset call args mock
    mock_db["customers"].find_one_and_update.reset_mock()

    # 2. Update address - set landmark to null
    payload_addr = {
        "landmark": None
    }
    response_addr = client.put("/api/v1/customers/me/addresses/addr-111", json=payload_addr)
    assert response_addr.status_code == 200

    called_args = mock_db["customers"].find_one_and_update.call_args[0]
    called_kwargs = mock_db["customers"].find_one_and_update.call_args[1]
    update_op = called_args[1] if len(called_args) > 1 else called_kwargs.get("update")
    assert update_op["$set"]["addresses"][0]["landmark"] is None

    app.dependency_overrides.clear()

