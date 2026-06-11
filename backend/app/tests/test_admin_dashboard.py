from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import Decimal128, ObjectId
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
            coll.aggregate = AsyncMock()
            collections[key] = coll
        return collections[key]

    db.__getitem__.side_effect = get_mock_collection
    return db


def create_mock_order_doc(
    order_id: str,
    order_status: str = "confirmed",
    fulfillment_status: str = "pending",
    payment_status: str = "paid",
) -> dict[str, Any]:
    return {
        "_id": ObjectId(order_id),
        "order_number": "MBF-20260606-000001",
        "checkout_id": "60c72b2f9b1d8e2a3c4f5e7b",
        "customer_id": "customer_123",
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
                "product_id": "product_123",
                "variant_id": "var_123",
                "sku": "HONEY-500G",
                "product_name": "Organic Honey",
                "variant_title": "500g",
                "quantity": 1,
                "unit_price": Decimal128("250.00"),
                "line_total": Decimal128("250.00"),
                "reserved_warehouse_id": "wh_1"
            }
        ],
        "pricing": {
            "subtotal": Decimal128("250.00"),
            "discount": Decimal128("0.00"),
            "tax_total": Decimal128("12.50"),
            "shipping_fee": Decimal128("50.00"),
            "grand_total": Decimal128("312.50")
        },
        "payment_status": payment_status,
        "fulfillment_status": fulfillment_status,
        "order_status": order_status,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


def create_mock_inventory_doc(
    inventory_id: str,
    sku: str,
    safety_stock: int,
    on_hand: int,
    reserved: int,
) -> dict[str, Any]:
    return {
        "_id": ObjectId(inventory_id),
        "sku": sku,
        "variant_id": "variant_123",
        "product_id": "product_123",
        "warehouse_stock": [
            {
                "warehouse_id": "wh_1",
                "on_hand": on_hand,
                "reserved": reserved,
                "location_code": "A-1"
            }
        ],
        "safety_stock_level": safety_stock,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


def create_mock_payment_doc(payment_id: str, status: str = "proof_submitted") -> dict[str, Any]:
    return {
        "_id": ObjectId(payment_id),
        "order_id": "60c72b2f9b1d8e2a3c4f5e7a",
        "order_number": "MBF-12345",
        "customer_id": "customer_123",
        "amount": Decimal128("300.00"),
        "upi_id": "merchant@upi",
        "upi_link": "upi://pay?...",
        "status": status,
        "screenshot_media_id": "media_123",
        "transaction_note": "Payment proof",
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


def create_mock_review_doc(review_id: str, status: str = "pending") -> dict[str, Any]:
    return {
        "_id": ObjectId(review_id),
        "product_id": "product_123",
        "customer_id": "customer_123",
        "order_id": "order_123",
        "rating": 5,
        "title": "Good product",
        "comment": "Nice taste",
        "is_verified_purchase": True,
        "moderation_status": status,
        "is_approved": False,
        "is_deleted": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


# --- Access Control Tests ---

@pytest.mark.anyio
async def test_customer_denied_access(mock_db: MagicMock) -> None:
    mock_customer = TokenData(
        user_id="customer_123",
        email="customer@example.test",
        role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.get("/api/v1/admin/dashboard")
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert " clearance" in response.json()["message"].lower()


@pytest.mark.anyio
async def test_warehouse_dashboard_limited_access(mock_db: MagicMock) -> None:
    # 1. Setup mock returns for operational fields
    mock_db["orders"].count_documents = AsyncMock(side_effect=lambda query: {
        "confirmed": 12,
        "shipped": 5,
        "delivered": 10
    }.get(query.get("order_status") or query.get("fulfillment_status"), 0))

    # Mock low stock alerts (1 alert)
    mock_inv = create_mock_inventory_doc("60c72b2f9b1d8e2a3c4f5e7c", "SKU-1", 10, 5, 0)
    mock_cursor_inv = MagicMock()
    mock_cursor_inv.__aiter__.return_value = [mock_inv]
    mock_db["inventories"].aggregate = AsyncMock(return_value=mock_cursor_inv)

    # Mock recent confirmed orders (1 order)
    mock_order = create_mock_order_doc("60c72b2f9b1d8e2a3c4f5e7d", order_status="confirmed")
    mock_cursor_ord = MagicMock()
    mock_cursor_ord.sort.return_value = mock_cursor_ord
    mock_cursor_ord.limit.return_value = mock_cursor_ord
    mock_cursor_ord.__aiter__.return_value = [mock_order]
    mock_db["orders"].find = MagicMock(return_value=mock_cursor_ord)

    # 2. Setup Warehouse role overrides
    mock_warehouse = TokenData(
        user_id="warehouse_123",
        email="warehouse@mrbharathfoods.in",
        role=UserRole.WAREHOUSE
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_warehouse

    # 3. Call endpoint
    response = client.get("/api/v1/admin/dashboard")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()["data"]

    # Operational data should be returned
    assert res_data["confirmed_orders"] == 12
    assert res_data["shipped_orders"] == 5
    assert res_data["delivered_orders"] == 10
    assert res_data["low_stock_count"] == 1
    assert len(res_data["low_stock_alerts"]) == 1
    assert len(res_data["recent_orders"]) == 1
    assert res_data["recent_orders"][0]["order_status"] == "confirmed"

    # Financial / admin metrics must be hidden (None)
    assert res_data["total_orders"] is None
    assert res_data["total_revenue"] is None
    assert res_data["pending_payments"] is None
    assert res_data["pending_review_count"] is None
    assert res_data["total_customers"] is None
    assert res_data["total_products"] is None
    assert res_data["pending_payment_proofs"] is None
    assert res_data["pending_reviews"] is None


@pytest.mark.anyio
async def test_admin_dashboard_full_access(mock_db: MagicMock) -> None:
    # 1. Setup mock returns for all summaries
    mock_db["orders"].count_documents = AsyncMock(side_effect=lambda query: {
        "confirmed": 15,
        "shipped": 8,
        "delivered": 20
    }.get(query.get("order_status") or query.get("fulfillment_status"), 50))  # Default 50 for total orders

    # Mock total customers and active products
    mock_db["customers"].count_documents = AsyncMock(return_value=120)
    mock_db["products"].count_documents = AsyncMock(return_value=45)

    # Mock low stock alerts (0 alerts)
    mock_cursor_inv = MagicMock()
    mock_cursor_inv.__aiter__.return_value = []
    mock_db["inventories"].aggregate = AsyncMock(return_value=mock_cursor_inv)

    # Mock revenue aggregation (e.g. 5000.00)
    mock_cursor_rev = MagicMock()
    mock_cursor_rev.__aiter__.return_value = [{"_id": None, "total_revenue": Decimal128("5000.00")}]
    mock_db["orders"].aggregate = AsyncMock(return_value=mock_cursor_rev)

    # Mock pending payments (2 pending)
    mock_db["payments"].count_documents = AsyncMock(return_value=2)
    mock_pay = create_mock_payment_doc("60c72b2f9b1d8e2a3c4f5e7e")
    mock_cursor_pay = MagicMock()
    mock_cursor_pay.sort.return_value = mock_cursor_pay
    mock_cursor_pay.limit.return_value = mock_cursor_pay
    mock_cursor_pay.__aiter__.return_value = [mock_pay]
    mock_db["payments"].find = MagicMock(return_value=mock_cursor_pay)

    # Mock pending reviews (3 pending)
    mock_db["reviews"].count_documents = AsyncMock(return_value=3)
    mock_rev = create_mock_review_doc("60c72b2f9b1d8e2a3c4f5e7f")
    mock_cursor_rev_list = MagicMock()
    mock_cursor_rev_list.sort.return_value = mock_cursor_rev_list
    mock_cursor_rev_list.limit.return_value = mock_cursor_rev_list
    mock_cursor_rev_list.__aiter__.return_value = [mock_rev]
    mock_db["reviews"].find = MagicMock(return_value=mock_cursor_rev_list)

    # Mock recent orders
    mock_order = create_mock_order_doc("60c72b2f9b1d8e2a3c4f5e7d")
    mock_cursor_ord = MagicMock()
    mock_cursor_ord.sort.return_value = mock_cursor_ord
    mock_cursor_ord.limit.return_value = mock_cursor_ord
    mock_cursor_ord.__aiter__.return_value = [mock_order]
    mock_db["orders"].find = MagicMock(return_value=mock_cursor_ord)

    # 2. Setup Admin role override
    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    # 3. Call endpoint
    response = client.get("/api/v1/admin/dashboard")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()["data"]

    # Assert all summaries are correctly calculated & returned
    assert res_data["total_orders"] == 50
    assert float(res_data["total_revenue"]) == 5000.00
    assert res_data["pending_payments"] == 2
    assert res_data["confirmed_orders"] == 15
    assert res_data["shipped_orders"] == 8
    assert res_data["delivered_orders"] == 20
    assert res_data["low_stock_count"] == 0
    assert res_data["pending_review_count"] == 3
    assert res_data["total_customers"] == 120
    assert res_data["total_products"] == 45
    assert len(res_data["recent_orders"]) == 1
    assert len(res_data["pending_payment_proofs"]) == 1
    assert len(res_data["pending_reviews"]) == 1


# --- Data Pipeline / Calculation Logic Tests ---

@pytest.mark.anyio
async def test_revenue_aggregation(mock_db: MagicMock) -> None:
    # Mock aggregation to yield total revenue sum
    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = [{"_id": None, "total_revenue": Decimal128("1250.75")}]
    mock_db["orders"].aggregate = AsyncMock(return_value=mock_cursor)

    # Call DashboardService directly
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.review_repository import ReviewRepository
    from app.services.dashboard_service import DashboardService

    service = DashboardService(
        order_repo=OrderRepository(mock_db),
        payment_repo=PaymentRepository(mock_db),
        inventory_repo=InventoryRepository(mock_db),
        review_repo=ReviewRepository(mock_db),
        customer_repo=CustomerRepository(mock_db),
        product_repo=ProductRepository(mock_db)
    )

    data = await service.get_dashboard_data(UserRole.ADMIN)
    assert data.total_revenue == Decimal("1250.75")


@pytest.mark.anyio
async def test_pending_proof_count(mock_db: MagicMock) -> None:
    # Mock count_documents return value
    mock_db["payments"].count_documents = AsyncMock(return_value=4)

    # Call DashboardService directly
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.review_repository import ReviewRepository
    from app.services.dashboard_service import DashboardService

    service = DashboardService(
        order_repo=OrderRepository(mock_db),
        payment_repo=PaymentRepository(mock_db),
        inventory_repo=InventoryRepository(mock_db),
        review_repo=ReviewRepository(mock_db),
        customer_repo=CustomerRepository(mock_db),
        product_repo=ProductRepository(mock_db)
    )

    data = await service.get_dashboard_data(UserRole.ADMIN)
    assert data.pending_payments == 4

    # Verify query status filter
    mock_db["payments"].count_documents.assert_called_with(
        {"status": "proof_submitted", "is_deleted": {"$ne": True}}
    )


@pytest.mark.anyio
async def test_low_stock_count(mock_db: MagicMock) -> None:
    # Mock two low stock items
    mock_inv1 = create_mock_inventory_doc("60c72b2f9b1d8e2a3c4f5e7a", "SKU-A", 15, 10, 0)
    mock_inv2 = create_mock_inventory_doc("60c72b2f9b1d8e2a3c4f5e7b", "SKU-B", 5, 2, 0)

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = [mock_inv1, mock_inv2]
    mock_db["inventories"].aggregate = AsyncMock(return_value=mock_cursor)

    # Call DashboardService directly
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.review_repository import ReviewRepository
    from app.services.dashboard_service import DashboardService

    service = DashboardService(
        order_repo=OrderRepository(mock_db),
        payment_repo=PaymentRepository(mock_db),
        inventory_repo=InventoryRepository(mock_db),
        review_repo=ReviewRepository(mock_db),
        customer_repo=CustomerRepository(mock_db),
        product_repo=ProductRepository(mock_db)
    )

    data = await service.get_dashboard_data(UserRole.ADMIN)
    assert data.low_stock_count == 2
    assert data.low_stock_alerts is not None
    assert len(data.low_stock_alerts) == 2
    assert data.low_stock_alerts[0].sku == "SKU-A"


@pytest.mark.anyio
async def test_pending_reviews_count(mock_db: MagicMock) -> None:
    # Mock count_documents return value
    mock_db["reviews"].count_documents = AsyncMock(return_value=7)

    # Call DashboardService directly
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.review_repository import ReviewRepository
    from app.services.dashboard_service import DashboardService

    service = DashboardService(
        order_repo=OrderRepository(mock_db),
        payment_repo=PaymentRepository(mock_db),
        inventory_repo=InventoryRepository(mock_db),
        review_repo=ReviewRepository(mock_db),
        customer_repo=CustomerRepository(mock_db),
        product_repo=ProductRepository(mock_db)
    )

    data = await service.get_dashboard_data(UserRole.ADMIN)
    assert data.pending_review_count == 7

    # Verify query state filter
    mock_db["reviews"].count_documents.assert_called_with(
        {"moderation_status": "pending", "is_deleted": {"$ne": True}}
    )
