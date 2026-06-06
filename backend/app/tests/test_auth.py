from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_db, get_redis
from app.core.roles import UserRole
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from main import app

client = TestClient(app)

# 1. Security Utilities Tests
def test_password_hashing() -> None:
    password = "SuperSecurePassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_generation_and_decoding() -> None:
    user_id = "507f1f77bcf86cd799439011"
    role = UserRole.CUSTOMER.value
    token = create_access_token(subject=user_id, role=role)

    payload = decode_access_token(token)
    assert payload.get("sub") == user_id
    assert payload.get("role") == role
    assert "exp" in payload

# 2. Mock Databases and cache dependecies for routing checks
@pytest.fixture  # type: ignore[untyped-decorator]
def mock_db() -> MagicMock:
    db = MagicMock()
    # Mock collections queries
    db["customers"] = MagicMock()
    return db

@pytest.fixture  # type: ignore[untyped-decorator]
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    # Mock redis get/set methods
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis

# 3. Router Integration Mocks
def test_register_flow(mock_db: MagicMock, mock_redis: AsyncMock) -> None:
    # Set up mock returns
    mock_db["customers"].find_one = AsyncMock(return_value=None)
    mock_db["customers"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011"))

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis

    payload = {
        "first_name": "Gowtham",
        "last_name": "Kumar",
        "email": "test@mrbharathfoods.in",
        "phone_number": "+919876543210",
        "password": "SecurePassword123!"
    }

    response = client.post("/api/v1/auth/register", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "test@mrbharathfoods.in"
    assert json_data["data"]["phone"] == "+919876543210"

def test_login_flow(mock_db: MagicMock, mock_redis: AsyncMock) -> None:
    hashed_pwd = get_password_hash("SecurePassword123!")
    customer_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "auth": {
            "email": "test@mrbharathfoods.in",
            "phone": "+919876543210",
            "password_hash": hashed_pwd,
            "status": "active",
            "role": "customer"
        },
        "personal_details": {
            "first_name": "Gowtham",
            "last_name": "Kumar"
        },
        "is_deleted": False
    }

    mock_db["customers"].find_one = AsyncMock(return_value=customer_doc)
    mock_db["customers"].find_one_and_update = AsyncMock(return_value=customer_doc)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis

    payload = {
        "email_or_phone": "+919876543210",
        "password": "SecurePassword123!"
    }

    response = client.post("/api/v1/auth/login", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert json_data["data"]["role"] == "customer"

def test_otp_request_flow(mock_redis: AsyncMock) -> None:
    app.dependency_overrides[get_redis] = lambda: mock_redis

    payload = {
        "phone_number": "+919876543210"
    }

    response = client.post("/api/v1/auth/otp/request", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "Verification code dispatched" in json_data["message"]
