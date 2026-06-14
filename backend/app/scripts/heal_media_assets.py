"""
One-time script: Heal missing media assets in MongoDB.
Ensure that the three missing production media IDs:
- 6a2d1180f8d9ad332876e91b (Rasipuram Pure Ghee)
- 6a2d1161f8d9ad332876e917 (Uthukuli A2 Cow Ghee)
- 6a2d7ca6d9bcabeeef61aad5 (Traditional Millet & Nut Energy Bar)
have valid completed media asset documents in the database.

This script is idempotent and will not overwrite valid existing Cloudinary/R2 URLs.

Run from the backend directory:
    python -m app.scripts.heal_media_assets
"""

import asyncio
from datetime import UTC, datetime

from bson import ObjectId
from pymongo import AsyncMongoClient

from app.core.config import settings

MISSING_MEDIA_ASSETS = [
    {
        "_id": ObjectId("6a2d1180f8d9ad332876e91b"),
        "original_filename": "rasipuram-ghee.jpg",
        "content_type": "image/jpeg",
        "size": 0,
        "storage_key": "media/product_image/admin/6a2d1180f8d9ad332876e91b-rasipuram-ghee.jpg",
        "public_url": "/images/rasipuram-ghee.jpg",
        "uploaded_by": "admin",
        "asset_type": "product_image",
        "status": "completed",
        "is_deleted": False,
        "deleted_at": None,
    },
    {
        "_id": ObjectId("6a2d1161f8d9ad332876e917"),
        "original_filename": "uthukuli-ghee.jpg",
        "content_type": "image/jpeg",
        "size": 0,
        "storage_key": "media/product_image/admin/6a2d1161f8d9ad332876e917-uthukuli-ghee.jpg",
        "public_url": "/images/uthukuli-ghee.jpg",
        "uploaded_by": "admin",
        "asset_type": "product_image",
        "status": "completed",
        "is_deleted": False,
        "deleted_at": None,
    },
    {
        "_id": ObjectId("6a2d7ca6d9bcabeeef61aad5"),
        "original_filename": "product-placeholder.jpg",
        "content_type": "image/jpeg",
        "size": 0,
        "storage_key": "media/product_image/admin/6a2d7ca6d9bcabeeef61aad5-product-placeholder.jpg",
        "public_url": "/images/product-placeholder.jpg",
        "uploaded_by": "admin",
        "asset_type": "product_image",
        "status": "completed",
        "is_deleted": False,
        "deleted_at": None,
    }
]


def is_valid_external_url(url: str) -> bool:
    if not url:
        return False
    url_lower = url.lower()
    # A valid external URL starts with http and belongs to Cloudinary, R2, or AWS/Cloudfront
    return (
        url_lower.startswith("http")
        and any(domain in url_lower for domain in ["cloudinary", "r2", "cloudflare", "amazonaws", "cloudfront"])
    )


async def run() -> None:
    client: AsyncMongoClient = AsyncMongoClient(settings.MONGODB_URI, tz_aware=True)  # type: ignore[type-arg]
    db = client[settings.DATABASE_NAME]
    collection = db["media_assets"]

    print("[heal_media_assets] Starting media assets validation/healing...")

    for asset_def in MISSING_MEDIA_ASSETS:
        asset_id = asset_def["_id"]
        existing = await collection.find_one({"_id": asset_id})

        if existing:
            current_url = existing.get("public_url", "")
            if is_valid_external_url(current_url):
                print(
                    f"[heal_media_assets] Media asset {asset_id} already has a valid "
                    f"external URL: {current_url}. Skipping overwrite."
                )
                continue
            else:
                # Update/overwrite fields if the current public_url is empty, a fallback path, or invalid
                update_fields = {k: v for k, v in asset_def.items() if k != "_id"}
                update_fields["updated_at"] = datetime.now(UTC)
                await collection.update_one({"_id": asset_id}, {"$set": update_fields})
                print(f"[heal_media_assets] Updated media asset {asset_id} with default local fallback.")
        else:
            # Document does not exist, insert it directly
            new_doc = dict(asset_def)
            new_doc["created_at"] = datetime.now(UTC)
            new_doc["updated_at"] = datetime.now(UTC)
            await collection.insert_one(new_doc)
            print(f"[heal_media_assets] Inserted new media asset {asset_id} with default local fallback.")

    await client.close()
    print("[heal_media_assets] Validation and healing complete.")


if __name__ == "__main__":
    asyncio.run(run())
