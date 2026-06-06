from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.core.settings_defaults import DEFAULT_SETTINGS
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


def create_mock_settings_doc(
    settings_id: str = "60c72b2f9b1d8e2a3c4f5e7a",
    upi_id: str = "db_upi@id",
    tax: Decimal = Decimal("12.00"),
    shipping: Decimal = Decimal("75.00"),
    free_shipping: Decimal = Decimal("750.00"),
) -> dict[str, Any]:
    return {
        "_id": ObjectId(settings_id),
        "upi_id": upi_id,
        "tax_percentage": tax,
        "shipping_fee": shipping,
        "free_shipping_threshold": free_shipping,
        "support_contact": "help@mrbharathfoods.in",
        "fssai_number": "12345678901234",
        "gst_number": "33AABCM1234D1Z5",
        "is_deleted": False,
        "created_at": datetime_now_utc(),
        "updated_at": datetime_now_utc(),
    }


def datetime_now_utc() -> Any:
    from datetime import UTC, datetime
    return datetime.now(UTC)


# --- Public settings endpoint tests ---

@pytest.mark.anyio
async def test_get_public_settings_default_fallback(mock_db: MagicMock) -> None:
    # 1. No settings doc exists in DB, triggers insert of default
    mock_db["settings"].find_one = AsyncMock(return_value=None)

    mock_insert_id = ObjectId("60c72b2f9b1d8e2a3c4f5e7a")
    async def mock_insert(doc: dict[str, Any]) -> Any:
        doc["_id"] = mock_insert_id
        result = MagicMock()
        result.inserted_id = mock_insert_id
        return result
    mock_db["settings"].insert_one = AsyncMock(side_effect=mock_insert)

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/settings/public")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()["data"]

    # Assert fallback constants are loaded
    assert float(res_data["tax_percentage"]) == float(DEFAULT_SETTINGS["tax_percentage"])
    assert float(res_data["shipping_fee"]) == float(DEFAULT_SETTINGS["shipping_fee"])
    assert float(res_data["free_shipping_threshold"]) == float(DEFAULT_SETTINGS["free_shipping_threshold"])
    assert res_data["support_contact"] == DEFAULT_SETTINGS["support_contact"]


@pytest.mark.anyio
async def test_get_public_settings_from_db(mock_db: MagicMock) -> None:
    # 1. Mock existing settings doc in DB
    mock_settings = create_mock_settings_doc()
    mock_db["settings"].find_one = AsyncMock(return_value=mock_settings)

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/settings/public")
    app.dependency_overrides.clear()

    assert response.status_code == 200, response.json()
    res_data = response.json()["data"]

    assert float(res_data["tax_percentage"]) == 12.00
    assert float(res_data["shipping_fee"]) == 75.00
    assert float(res_data["free_shipping_threshold"]) == 750.00
    assert "upi_id" not in res_data  # Public response hides UPI ID


# --- Admin Endpoint Access Control Tests ---

@pytest.mark.anyio
async def test_customer_denied_admin_settings_get(mock_db: MagicMock) -> None:
    mock_customer = TokenData(
        user_id="customer_123",
        email="customer@mrbharathfoods.in",
        role=UserRole.CUSTOMER
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_customer

    response = client.get("/api/v1/admin/settings")
    app.dependency_overrides.clear()

    assert response.status_code == 403


@pytest.mark.anyio
async def test_admin_settings_get_and_update(mock_db: MagicMock) -> None:
    mock_settings = create_mock_settings_doc()
    mock_db["settings"].find_one = AsyncMock(return_value=mock_settings)
    mock_db["audit_logs"].insert_one = AsyncMock()

    # 1. Test GET Admin settings
    mock_admin = TokenData(
        user_id="admin_123",
        email="admin@mrbharathfoods.in",
        role=UserRole.ADMIN
    )
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    response_get = client.get("/api/v1/admin/settings")
    assert response_get.status_code == 200, response_get.json()
    assert response_get.json()["data"]["upi_id"] == "db_upi@id"  # Visible to admin

    # 2. Test PATCH Admin settings
    updated_doc = mock_settings.copy()
    updated_doc["upi_id"] = "new_upi@id"
    updated_doc["tax_percentage"] = Decimal("15.00")

    mock_db["settings"].find_one_and_update = AsyncMock(return_value=updated_doc)

    payload = {
        "upi_id": "new_upi@id",
        "tax_percentage": "15.00"
    }
    response_patch = client.patch("/api/v1/admin/settings", json=payload)
    app.dependency_overrides.clear()

    assert response_patch.status_code == 200, response_patch.json()
    assert response_patch.json()["data"]["upi_id"] == "new_upi@id"
    assert float(response_patch.json()["data"]["tax_percentage"]) == 15.00

    # Assert audit log was generated
    mock_db["audit_logs"].insert_one.assert_called_once()
    assert mock_db["audit_logs"].insert_one.call_args[0][0]["action"] == "UPDATE_SETTINGS"


# --- Service Integration Overrides Validation Tests ---

@pytest.mark.anyio
async def test_payment_upi_id_settings_override(mock_db: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    # 1. Custom UPI ID configured in DB
    mock_settings = create_mock_settings_doc(upi_id="custom_database_upi@id")
    mock_db["settings"].find_one = AsyncMock(return_value=mock_settings)

    # 2. Setup mock order
    from bson import ObjectId
    order_doc = {
        "_id": ObjectId("60c72b2f9b1d8e2a3c4f5e7b"),
        "order_number": "MBF-99999",
        "checkout_id": "checkout_123",
        "customer_id": "customer_123",
        "customer_snapshot": {"email": "customer@mrbharathfoods.in"},
        "shipping_address_snapshot": {
            "full_name": "Test Customer", "phone": "123", "address_line1": "123",
            "city": "Chennai", "state": "TN", "pincode": "123", "country": "India"
        },
        "items": [],
        "pricing": {
            "subtotal": Decimal("200.00"),
            "discount": Decimal("0.00"),
            "tax_total": Decimal("10.00"),
            "shipping_fee": Decimal("50.00"),
            "grand_total": Decimal("260.00")
        },
        "payment_status": "pending",
        "fulfillment_status": "pending",
        "order_status": "pending_payment",
        "is_deleted": False,
        "created_at": datetime_now_utc(),
        "updated_at": datetime_now_utc()
    }
    mock_db["orders"].find_one = AsyncMock(return_value=order_doc)
    mock_db["payments"].find_one = AsyncMock(return_value=None)
    mock_db["payments"].insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId("60c72b2f9b1d8e2a3c4f5e7c")))
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Call initiate payment via service
    from app.repositories.media_repository import MediaRepository
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.services.payment_service import PaymentService

    mock_audit = MagicMock()
    mock_audit.log_action = AsyncMock()

    service = PaymentService(
        repository=PaymentRepository(mock_db),
        order_repository=OrderRepository(mock_db),
        media_repository=MediaRepository(mock_db),
        audit_service=mock_audit
    )

    token = TokenData(user_id="customer_123", email="customer@mrbharathfoods.in", role=UserRole.CUSTOMER)
    payment = await service.initiate_upi_payment(order_id="60c72b2f9b1d8e2a3c4f5e7b", current_user=token)

    # Assert deep link uses custom UPI ID
    assert payment.upi_id == "custom_database_upi@id"
    assert "pa=custom_database_upi%40id" in payment.upi_link or "pa=custom_database_upi@id" in payment.upi_link


@pytest.mark.anyio
async def test_checkout_tax_and_shipping_override(mock_db: MagicMock) -> None:
    # 1. Custom settings: 10% tax, 100.00 shipping, 1000.00 free shipping limit
    mock_settings = create_mock_settings_doc(
        tax=Decimal("10.00"),
        shipping=Decimal("100.00"),
        free_shipping=Decimal("1000.00")
    )
    mock_db["settings"].find_one = AsyncMock(return_value=mock_settings)

    # 2. Mock Cart (containing 1 item worth 500.00)
    cart_doc = {
        "_id": ObjectId("60c72b2f9b1d8e2a3c4f5e7b"),
        "customer_id": "customer_123",
        "items": [
            {
                "product_id": "60c72b2f9b1d8e2a3c4f5e71",
                "variant_id": "60c72b2f9b1d8e2a3c4f5e72",
                "sku": "HONEY-1",
                "quantity": 1,
                "unit_price_snapshot": Decimal("500.00")
            }
        ],
        "created_at": datetime_now_utc(),
        "updated_at": datetime_now_utc(),
        "is_deleted": False
    }
    mock_db["carts"].find_one = AsyncMock(return_value=cart_doc)

    # Mock product & variant
    product_doc = {
        "_id": ObjectId("60c72b2f9b1d8e2a3c4f5e71"),
        "name": "Super Honey",
        "slug": "super-honey",
        "description": "Super Honey description",
        "short_description": "Super Honey short desc",
        "category_id": "60c72b2f9b1d8e2a3c4f5e70",
        "sourcing": {
            "region": "Kashmir",
            "story": "Kashmiri honey"
        },
        "variants": [
            {
                "variant_id": "60c72b2f9b1d8e2a3c4f5e72",
                "sku": "HONEY-1",
                "title": "500g",
                "volume_weight": "500g",
                "price": Decimal("500.00"),
                "is_active": True
            }
        ],
        "is_deleted": False,
        "status": "active"
    }
    mock_db["products"].find_one = AsyncMock(return_value=product_doc)

    # Mock stock
    inventory_doc = {
        "_id": ObjectId("60c72b2f9b1d8e2a3c4f5e73"),
        "sku": "HONEY-1",
        "product_id": "60c72b2f9b1d8e2a3c4f5e71",
        "variant_id": "60c72b2f9b1d8e2a3c4f5e72",
        "warehouse_stock": [{"warehouse_id": "WH-1", "on_hand": 5, "reserved": 0}],
        "safety_stock_level": 1,
        "is_deleted": False
    }
    mock_db["inventories"].find_one = AsyncMock(return_value=inventory_doc)
    mock_db["inventories"].find_one_and_update = AsyncMock(return_value=inventory_doc)
    mock_db["checkouts"].insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId("60c72b2f9b1d8e2a3c4f5e7d")))
    mock_db["audit_logs"].insert_one = AsyncMock()

    # Call checkout service
    from app.repositories.cart_repository import CartRepository
    from app.repositories.checkout_repository import CheckoutRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.product_repository import ProductRepository
    from app.services.checkout_service import CheckoutService
    from app.services.inventory_service import InventoryService

    mock_audit = MagicMock()
    mock_audit.log_action = AsyncMock()

    inv_service = InventoryService(
        repository=InventoryRepository(mock_db),
        product_repository=ProductRepository(mock_db),
        audit_service=mock_audit
    )
    service = CheckoutService(
        repository=CheckoutRepository(mock_db),
        cart_repository=CartRepository(mock_db),
        product_repository=ProductRepository(mock_db),
        inventory_repository=InventoryRepository(mock_db),
        inventory_service=inv_service,
        audit_service=mock_audit
    )

    from app.schemas.checkout import ShippingAddressSchema
    address = ShippingAddressSchema(
        full_name="John", phone="9876543210", address_line1="Street", city="City", state="State", pincode="600001"
    )

    session = await service.initiate_checkout(
        cart_id="60c72b2f9b1d8e2a3c4f5e7b",
        customer_id="customer_123",
        email="customer@mrbharathfoods.in",
        shipping_address=address,
        idempotency_key="test-key"
    )

    # Assert pricing based on custom DB settings (10% tax, 100.00 shipping)
    # subtotal = 500.00
    # tax = 500.00 * 0.10 = 50.00
    # shipping = 100.00 (since 500.00 < 1000.00 free shipping limit)
    # grand_total = 500.00 + 50.00 + 100.00 = 650.00
    assert session.subtotal == Decimal("500.00")
    assert session.tax_estimate == Decimal("50.00")
    assert session.shipping_fee == Decimal("100.00")
    assert session.grand_total == Decimal("650.00")
