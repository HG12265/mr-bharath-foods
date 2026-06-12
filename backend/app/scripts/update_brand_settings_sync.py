"""
One-time migration script: Update existing AppSettings document in MongoDB Atlas
to reflect the new brand name: Bharath Delight Foods.

Run from the backend directory using:
    py -3 app/scripts/update_brand_settings_sync.py

This script uses synchronous pymongo (no motor required).
This script is idempotent — safe to run multiple times.
"""

import os
import sys
from datetime import UTC, datetime

# Add backend directory to path so config can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

MONGODB_URI = os.environ.get("MONGODB_URI", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mr_bharath_foods")

if not MONGODB_URI:
    print("[update_brand_settings] ERROR: MONGODB_URI not found in environment.")
    sys.exit(1)

BRAND_UPDATE_FIELDS = {
    "brand_name": "Bharath Delight Foods",
    "payment_display_name": "Bharath Delight Foods",
    "support_contact": "support@bharathdelightfoods.in",
    "support_email": "support@bharathdelightfoods.in",
    "public_support_email": "support@bharathdelightfoods.in",
    "updated_at": datetime.now(UTC),
}


def run() -> None:
    from pymongo import MongoClient

    print(f"[update_brand_settings] Connecting to database: {DATABASE_NAME}")
    client: MongoClient = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["settings"]

    existing = collection.find_one({})
    if not existing:
        print("[update_brand_settings] No AppSettings document found. "
              "Run seed_production.py first to initialize settings.")
        client.close()
        return

    doc_id = existing["_id"]
    result = collection.update_one(
        {"_id": doc_id},
        {"$set": BRAND_UPDATE_FIELDS}
    )

    if result.modified_count > 0:
        print(f"[update_brand_settings] SUCCESS: AppSettings document (id={doc_id}) "
              "updated to Bharath Delight Foods brand successfully.")
    else:
        print(f"[update_brand_settings] INFO: AppSettings document (id={doc_id}) "
              "was already up to date — no changes needed.")

    client.close()


if __name__ == "__main__":
    run()
