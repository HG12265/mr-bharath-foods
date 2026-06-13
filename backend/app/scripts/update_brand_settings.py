"""
One-time migration script: Update existing AppSettings document in MongoDB Atlas
to reflect the new brand name: Bharath Delight Foods.

Run from the backend directory:
    python -m app.scripts.update_brand_settings

This script is idempotent — safe to run multiple times.
"""

import asyncio
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

BRAND_UPDATE_FIELDS = {
    "brand_name": "Bharath Delight Foods",
    "payment_display_name": "Bharath Delight Foods",
    "support_contact": "support@bharathdelightfoods.in",
    "support_email": "support@bharathdelightfoods.in",
    "public_support_email": "support@bharathdelightfoods.in",
    "updated_at": datetime.now(UTC),
}


async def run() -> None:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI)  # type: ignore[var-annotated]
    db = client[settings.DATABASE_NAME]
    collection = db["settings"]

    existing = await collection.find_one({})
    if not existing:
        print("[update_brand_settings] No AppSettings document found. "
              "Run seed_production.py first to initialize settings.")
        client.close()
        return

    doc_id = existing["_id"]
    result = await collection.update_one(
        {"_id": doc_id},
        {"$set": BRAND_UPDATE_FIELDS}
    )

    if result.modified_count > 0:
        print(f"[update_brand_settings] ✅ AppSettings document (id={doc_id}) "
              "updated to Bharath Delight Foods brand successfully.")
    else:
        print(f"[update_brand_settings] [INFO] AppSettings document (id={doc_id}) "
              "was already up to date — no changes needed.")

    client.close()


if __name__ == "__main__":
    asyncio.run(run())
