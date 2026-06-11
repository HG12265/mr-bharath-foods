from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db
from app.core.rating_calculator import calculate_ratings_summary
from app.core.review_status import ReviewModerationStatus
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
    collections = {}

    def get_mock_collection(key: str) -> MagicMock:
        if key not in collections:
            coll = MagicMock()
            coll.insert_one = AsyncMock()
            coll.find_one = AsyncMock(return_value=None)
            coll.find_one_and_update = AsyncMock(return_value=None)
            coll.update_many = AsyncMock()
            coll.update_one = AsyncMock()
            collections[key] = coll
        return collections[key]

    db.__getitem__.side_effect = get_mock_collection
    return db


def create_mock_product_doc(product_id: str) -> dict[str, Any]:
    return {
        "_id": ObjectId(product_id),
        "name": "Organic Honey",
        "slug": "organic-honey",
        "description": "Pure premium organic honey sourced from local forests.",
        "short_description": "Pure organic honey.",
        "category_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "media_ids": [],
        "sourcing": {
            "region": "Western Ghats",
            "story": "Sourced from native bees in clean pastures."
        },
        "attributes": [],
        "variants": [],
        "seo": {
            "meta_title": None,
            "meta_description": None,
            "meta_keywords": []
        },
        "ratings": {
            "average_rating": 0.0,
            "review_count": 0,
            "total_reviews": 0,
            "star_1_count": 0,
            "star_2_count": 0,
            "star_3_count": 0,
            "star_4_count": 0,
            "star_5_count": 0
        },
        "tags": [],
        "search_keywords": [],
        "is_featured": False,
        "status": "active",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


def create_mock_order_doc(
    order_id: str,
    customer_id: str,
    product_id: str,
    fulfillment_status: str = "delivered"
) -> dict[str, Any]:
    return {
        "_id": ObjectId(order_id),
        "order_number": "MBF-20260606-000001",
        "checkout_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "customer_id": customer_id,
        "customer_snapshot": {
            "email": "customer@example.test"
        },
        "shipping_address_snapshot": {
            "full_name": "John Doe",
            "phone": "9876543210",
            "address_line1": "123 St",
            "city": "Chennai",
            "state": "TN",
            "pincode": "600001",
            "country": "India"
        },
        "items": [
            {
                "product_id": product_id,
                "variant_id": "var_123",
                "sku": "HONEY-500G",
                "product_name": "Organic Honey",
                "variant_title": "500g",
                "quantity": 1,
                "unit_price": Decimal("250.00"),
                "line_total": Decimal("250.00"),
                "reserved_warehouse_id": "wh_1"
            }
        ],
        "pricing": {
            "subtotal": Decimal("250.00"),
            "discount": Decimal("0.00"),
            "tax_total": Decimal("12.50"),
            "shipping_fee": Decimal("50.00"),
            "grand_total": Decimal("312.50")
        },
        "payment_status": "paid",
        "fulfillment_status": fulfillment_status,
        "order_status": "confirmed",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


def create_mock_review_doc(
    review_id: str,
    product_id: str,
    customer_id: str,
    order_id: str,
    rating: int = 5,
    moderation_status: str = "pending",
    is_approved: bool = False,
    is_deleted: bool = False,
    created_at: datetime | None = None
) -> dict[str, Any]:
    if created_at is None:
        created_at = datetime.now(UTC)
    return {
        "_id": ObjectId(review_id),
        "product_id": product_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "rating": rating,
        "title": "Amazing Organic Honey",
        "comment": "Tasted absolutely natural. Will buy again!",
        "is_verified_purchase": True,
        "moderation_status": moderation_status,
        "is_approved": is_approved,
        "is_deleted": is_deleted,
        "created_at": created_at,
        "updated_at": datetime.now(UTC)
    }


# --- Rating Calculator Tests ---

def test_calculate_ratings_summary_empty() -> None:
    res = calculate_ratings_summary([])
    assert res["average_rating"] == 0.0
    assert res["total_reviews"] == 0
    assert res["star_1_count"] == 0
    assert res["star_5_count"] == 0


def test_calculate_ratings_summary_values() -> None:
    class MockReview:
        def __init__(self, rating: int):
            self.rating = rating

    reviews = [
        MockReview(5),
        MockReview(5),
        MockReview(4),
        {"rating": 3},
        {"rating": 1}
    ]
    res = calculate_ratings_summary(reviews)
    assert res["total_reviews"] == 5
    assert res["average_rating"] == 3.6  # (5+5+4+3+1)/5 = 18/5 = 3.6
    assert res["star_5_count"] == 2
    assert res["star_4_count"] == 1
    assert res["star_3_count"] == 1
    assert res["star_2_count"] == 0
    assert res["star_1_count"] == 1


# --- Submit Review Tests ---

@pytest.mark.anyio
async def test_submit_review_success(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"
    customer_id = "customer_123"

    product_doc = create_mock_product_doc(product_id)
    order_doc = create_mock_order_doc(order_id, customer_id, product_id)

    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["reviews"].find_one = AsyncMock(return_value=None)  # No existing review

    mock_db["reviews"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=ObjectId("60c72b2f9b1d8e2a3c4f5e7e"))
    )
    mock_db["notifications"].insert_one = AsyncMock()
    mock_db["audit_logs"].insert_one = AsyncMock()

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "product_id": product_id,
        "order_id": order_id,
        "rating": 5,
        "title": "Fresh Honey",
        "comment": "Extremely pure and fresh honey."
    }

    response = client.post("/api/v1/reviews", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["product_id"] == product_id
    assert res_data["data"]["order_id"] == order_id
    assert res_data["data"]["rating"] == 5
    assert res_data["data"]["moderation_status"] == ReviewModerationStatus.PENDING.value
    assert res_data["data"]["is_approved"] is False


@pytest.mark.anyio
async def test_submit_review_product_not_found(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    mock_db["products"].find_one = AsyncMock(return_value=None)

    mock_customer = TokenData(
        user_id="customer_123",
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "product_id": product_id,
        "order_id": order_id,
        "rating": 5,
        "title": "Fresh Honey",
        "comment": "Extremely pure and fresh honey."
    }

    response = client.post("/api/v1/reviews", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()


@pytest.mark.anyio
async def test_submit_review_order_not_delivered(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"
    customer_id = "customer_123"

    product_doc = create_mock_product_doc(product_id)
    # Order status is packed instead of delivered
    order_doc = create_mock_order_doc(order_id, customer_id, product_id, fulfillment_status="packed")

    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["reviews"].find_one = AsyncMock(return_value=None)

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "product_id": product_id,
        "order_id": order_id,
        "rating": 5,
        "title": "Fresh Honey",
        "comment": "Extremely pure and fresh honey."
    }

    response = client.post("/api/v1/reviews", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "delivered" in response.json()["message"].lower()


@pytest.mark.anyio
async def test_submit_review_product_not_in_order(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    another_product_id = "60c72b2f9b1d8e2a3c4f5e7z"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"
    customer_id = "customer_123"

    product_doc = create_mock_product_doc(product_id)
    # Order contains another_product_id, not product_id
    order_doc = create_mock_order_doc(order_id, customer_id, another_product_id)

    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["reviews"].find_one = AsyncMock(return_value=None)

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "product_id": product_id,
        "order_id": order_id,
        "rating": 5,
        "title": "Fresh Honey",
        "comment": "Extremely pure and fresh honey."
    }

    response = client.post("/api/v1/reviews", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "does not belong" in response.json()["message"].lower()


@pytest.mark.anyio
async def test_submit_review_duplicate(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"
    customer_id = "customer_123"

    product_doc = create_mock_product_doc(product_id)
    order_doc = create_mock_order_doc(order_id, customer_id, product_id)
    existing_review = create_mock_review_doc(
        "60c72b2f9b1d8e2a3c4f5e7e", product_id, customer_id, order_id
    )

    mock_db["products"].find_one = AsyncMock(return_value=product_doc)
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["reviews"].find_one = AsyncMock(return_value=existing_review)

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "product_id": product_id,
        "order_id": order_id,
        "rating": 5,
        "title": "Fresh Honey",
        "comment": "Extremely pure and fresh honey."
    }

    response = client.post("/api/v1/reviews", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "already submitted" in response.json()["message"].lower()


# --- Edit Review Tests ---

@pytest.mark.anyio
async def test_edit_review_success(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    # Pending review edit
    review_doc = create_mock_review_doc(review_id, product_id, customer_id, order_id, rating=5)

    updated_review_doc = review_doc.copy()
    updated_review_doc["rating"] = 4
    updated_review_doc["title"] = "Updated Title"
    updated_review_doc["comment"] = "Updated comment here."

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)
    mock_db["reviews"].find_one_and_update = AsyncMock(return_value=updated_review_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "rating": 4,
        "title": "Updated Title",
        "comment": "Updated comment here."
    }

    response = client.patch(f"/api/v1/reviews/{review_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["rating"] == 4
    assert res_data["data"]["title"] == "Updated Title"
    assert res_data["data"]["comment"] == "Updated comment here."


@pytest.mark.anyio
async def test_edit_review_expired_30_days(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    # Created 31 days ago
    created_at = datetime.now(UTC) - timedelta(days=31)
    review_doc = create_mock_review_doc(
        review_id, product_id, customer_id, order_id, rating=5, created_at=created_at
    )

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    payload = {
        "rating": 4,
        "title": "Updated Title",
        "comment": "Updated comment here."
    }

    response = client.patch(f"/api/v1/reviews/{review_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "only be edited within 30 days" in response.json()["message"].lower()


@pytest.mark.anyio
async def test_edit_review_unauthorized_customer(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    review_doc = create_mock_review_doc(review_id, product_id, customer_id, order_id, rating=5)

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)

    # Different customer logged in
    mock_other_customer = TokenData(
        user_id="customer_999",
        email="other@mrbharathfoods.in",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_other_customer

    payload = {
        "rating": 4,
        "title": "Updated Title",
        "comment": "Updated comment here."
    }

    response = client.patch(f"/api/v1/reviews/{review_id}", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "authorized" in response.json()["message"].lower()


# --- Soft Delete Review Tests ---

@pytest.mark.anyio
async def test_delete_review_success_by_owner(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    review_doc = create_mock_review_doc(review_id, product_id, customer_id, order_id, is_approved=True)

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)

    # Assert soft delete happens
    soft_deleted_doc = review_doc.copy()
    soft_deleted_doc["is_deleted"] = True
    soft_deleted_doc["deleted_at"] = datetime.now(UTC)

    mock_db["reviews"].find_one_and_update = AsyncMock(return_value=soft_deleted_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Recalculate ratings mock
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.__aiter__.return_value = []  # No other reviews left
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor)
    mock_db["products"].update_one = AsyncMock()

    mock_customer = TokenData(
        user_id=customer_id,
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.delete(f"/api/v1/reviews/{review_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert response.json()["success"] is True

    # Verify soft delete call included setting is_deleted=True
    called_args = mock_db["reviews"].find_one_and_update.call_args[0][1]
    assert called_args["$set"]["is_deleted"] is True
    assert "deleted_at" in called_args["$set"]


# --- Admin Moderation Tests ---

@pytest.mark.anyio
async def test_admin_list_reviews(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    review_doc = create_mock_review_doc(review_id, "prod_1", "cust_1", "ord_1")

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__aiter__.return_value = [review_doc]
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor)

    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    response = client.get("/api/v1/admin/reviews")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["id"] == review_id


@pytest.mark.anyio
async def test_admin_approve_review_success(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    review_doc = create_mock_review_doc(review_id, product_id, customer_id, order_id, moderation_status="pending")

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)

    approved_doc = review_doc.copy()
    approved_doc["moderation_status"] = ReviewModerationStatus.APPROVED.value
    approved_doc["is_approved"] = True

    mock_db["reviews"].find_one_and_update = AsyncMock(return_value=approved_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()
    mock_db["notifications"].insert_one = AsyncMock()

    # Recalculate ratings setup
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.__aiter__.return_value = [approved_doc]
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor)
    mock_db["products"].update_one = AsyncMock()

    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    response = client.patch(f"/api/v1/admin/reviews/{review_id}/approve")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["data"]["is_approved"] is True
    assert res_data["data"]["moderation_status"] == ReviewModerationStatus.APPROVED.value

    # Verify ratings recalculation was triggered
    mock_db["products"].update_one.assert_called_once()
    set_payload = mock_db["products"].update_one.call_args[0][1]["$set"]["ratings"]
    assert set_payload["average_rating"] == 5.0
    assert set_payload["total_reviews"] == 1
    assert set_payload["star_5_count"] == 1


@pytest.mark.anyio
async def test_admin_reject_review_success(mock_db: MagicMock) -> None:
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    customer_id = "customer_123"
    order_id = "60c72b2f9b1d8e2a3c4f5e7d"

    # Previously approved review
    review_doc = create_mock_review_doc(
        review_id, product_id, customer_id, order_id, moderation_status="approved", is_approved=True
    )

    mock_db["reviews"].find_one = AsyncMock(return_value=review_doc)

    rejected_doc = review_doc.copy()
    rejected_doc["moderation_status"] = ReviewModerationStatus.REJECTED.value
    rejected_doc["is_approved"] = False

    mock_db["reviews"].find_one_and_update = AsyncMock(return_value=rejected_doc)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Recalculate ratings setup (empty reviews left)
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.__aiter__.return_value = []
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor)
    mock_db["products"].update_one = AsyncMock()

    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    response = client.patch(f"/api/v1/admin/reviews/{review_id}/reject")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["data"]["is_approved"] is False
    assert res_data["data"]["moderation_status"] == ReviewModerationStatus.REJECTED.value

    # Verify ratings recalculation was triggered
    mock_db["products"].update_one.assert_called_once()
    set_payload = mock_db["products"].update_one.call_args[0][1]["$set"]["ratings"]
    assert set_payload["average_rating"] == 0.0
    assert set_payload["total_reviews"] == 0


# --- Get Product Reviews Tests ---

@pytest.mark.anyio
async def test_get_product_reviews_success(mock_db: MagicMock) -> None:
    product_id = "60c72b2f9b1d8e2a3c4f5e7c"
    review_id = "60c72b2f9b1d8e2a3c4f5e7e"

    product_doc = create_mock_product_doc(product_id)
    product_doc["ratings"]["average_rating"] = 5.0
    product_doc["ratings"]["total_reviews"] = 1
    product_doc["ratings"]["star_5_count"] = 1

    review_doc = create_mock_review_doc(
        review_id, product_id, "customer_123", "order_123", rating=5, moderation_status="approved", is_approved=True
    )

    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.__aiter__.return_value = [review_doc]
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor)

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get(f"/api/v1/reviews/product/{product_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["product"]["name"] == "Organic Honey"
    assert res_data["data"]["ratings"]["average"] == 5.0
    assert res_data["data"]["ratings"]["total"] == 1
    assert len(res_data["data"]["reviews"]) == 1
    assert res_data["data"]["reviews"][0]["id"] == review_id
    assert res_data["data"]["reviews"][0]["is_approved"] is True
