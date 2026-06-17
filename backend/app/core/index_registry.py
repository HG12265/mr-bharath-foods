from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import (
    COLLECTION_CARTS,
    COLLECTION_CATEGORIES,
    COLLECTION_CUSTOMERS,
    COLLECTION_INVENTORIES,
    COLLECTION_NOTIFICATIONS,
    COLLECTION_ORDERS,
    COLLECTION_PAYMENTS,
    COLLECTION_PRODUCTS,
    COLLECTION_REVIEWS,
    COLLECTION_SHIPMENTS,
)
from app.core.logging import logger


async def initialize_indexes(db: AsyncDatabase) -> None:  # type: ignore[type-arg]
    """
    Registers and initializes all critical database indexes for Bharath Delight Foods.
    """
    logger.info("Initializing system database indexes...")

    # 1. Customers
    try:
        await db[COLLECTION_CUSTOMERS].create_index([("auth.email", ASCENDING)], unique=True, sparse=True)
        await db[COLLECTION_CUSTOMERS].create_index([("auth.phone", ASCENDING)], unique=True)
        logger.info("Customers indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating customers indexes: {exc}")

    # 2. Products
    try:
        await db[COLLECTION_PRODUCTS].create_index([("slug", ASCENDING)], unique=True)
        await db[COLLECTION_PRODUCTS].create_index([("category_id", ASCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("status", ASCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("is_deleted", ASCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("is_featured", ASCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("created_at", DESCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("name", ASCENDING)])
        await db[COLLECTION_PRODUCTS].create_index([("min_price", ASCENDING)])
        logger.info("Products indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating products indexes: {exc}")

    # One-time migration/backfill of min_price and display_price
    try:
        cursor = db[COLLECTION_PRODUCTS].find({"min_price": {"$exists": False}, "is_deleted": {"$ne": True}})
        async for doc in cursor:
            variants = doc.get("variants", [])
            active_prices = []
            for v in variants:
                if v.get("is_active", True):
                    price_val = v.get("price")
                    if price_val is not None:
                        active_prices.append(float(str(price_val)))
            if active_prices:
                m_price = min(active_prices)
                from bson.decimal128 import Decimal128
                await db[COLLECTION_PRODUCTS].update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"min_price": Decimal128(str(m_price)), "display_price": Decimal128(str(m_price))}}
                )
        logger.info("Product min_price/display_price migration completed.")
    except Exception as exc:
        logger.error(f"Error migrating product prices: {exc}")

    # 3. Orders
    try:
        await db[COLLECTION_ORDERS].create_index([("order_number", ASCENDING)], unique=True)
        await db[COLLECTION_ORDERS].create_index([("customer_id", ASCENDING)])
        await db[COLLECTION_ORDERS].create_index([("checkout_id", ASCENDING)])
        await db[COLLECTION_ORDERS].create_index([("order_status", ASCENDING)])
        await db[COLLECTION_ORDERS].create_index([("created_at", DESCENDING)])
        logger.info("Orders indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating orders indexes: {exc}")

    # 4. Carts
    try:
        await db[COLLECTION_CARTS].create_index([("customer_id", ASCENDING)])
        await db[COLLECTION_CARTS].create_index([("guest_token", ASCENDING)])
        await db[COLLECTION_CARTS].create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
        logger.info("Carts indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating carts indexes: {exc}")

    # 5. Payments
    try:
        await db[COLLECTION_PAYMENTS].create_index([("order_id", ASCENDING)])
        await db[COLLECTION_PAYMENTS].create_index([("status", ASCENDING)])
        logger.info("Payments indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating payments indexes: {exc}")

    # 6. Shipments
    try:
        await db[COLLECTION_SHIPMENTS].create_index([("order_id", ASCENDING)], unique=True)
        await db[COLLECTION_SHIPMENTS].create_index([("tracking_number", ASCENDING)])
        await db[COLLECTION_SHIPMENTS].create_index([("status", ASCENDING)])
        logger.info("Shipments indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating shipments indexes: {exc}")

    # 7. Reviews
    try:
        await db[COLLECTION_REVIEWS].create_index([("product_id", ASCENDING)])
        await db[COLLECTION_REVIEWS].create_index([("customer_id", ASCENDING)])
        await db[COLLECTION_REVIEWS].create_index([("moderation_status", ASCENDING)])
        # Partial unique index for active reviews on product_id + customer_id where is_deleted=false
        await db[COLLECTION_REVIEWS].create_index(
            [("product_id", ASCENDING), ("customer_id", ASCENDING)],
            unique=True,
            partialFilterExpression={"is_deleted": {"$eq": False}}
        )
        logger.info("Reviews indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating reviews indexes: {exc}")

    # 8. Notifications
    try:
        await db[COLLECTION_NOTIFICATIONS].create_index([("target_user_id", ASCENDING)])
        await db[COLLECTION_NOTIFICATIONS].create_index([("role_target", ASCENDING)])
        await db[COLLECTION_NOTIFICATIONS].create_index([("is_read", ASCENDING)])
        await db[COLLECTION_NOTIFICATIONS].create_index([("created_at", DESCENDING)])
        logger.info("Notifications indexes initialized.")
    except Exception as exc:
        logger.error(f"Error creating notifications indexes: {exc}")

    # 9. Inventories
    try:
        await db[COLLECTION_INVENTORIES].create_index([("sku", ASCENDING)], unique=True)
        logger.info("Inventories SKU unique index initialized.")
    except Exception as exc:
        logger.error(f"Error creating inventories index: {exc}")

    # 10. Categories
    try:
        await db[COLLECTION_CATEGORIES].create_index([("slug", ASCENDING)], unique=True)
        logger.info("Categories unique index on slug initialized.")
    except Exception as exc:
        logger.error(f"Error creating categories index: {exc}")

    logger.info("All system database indexes check completed.")
