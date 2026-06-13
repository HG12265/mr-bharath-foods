"""
One-time script: Update the existing admin user's email and password in MongoDB.

Run from the backend directory:
    py -3 app/scripts/update_admin_credentials.py
"""

import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

MONGODB_URI = os.environ.get("MONGODB_URI", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mr_bharath_foods")
NEW_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "bharathdelightfoods@gmail.com")
NEW_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "bharath123@")
OLD_ADMIN_EMAIL = "admin@mrbharathfoods.in"

if not MONGODB_URI:
    print("ERROR: MONGODB_URI not found in environment.")
    sys.exit(1)


def hash_password(password: str) -> str:
    """Hash password using bcrypt (same as app)."""
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def run() -> None:
    from pymongo import MongoClient

    print(f"Connecting to database: {DATABASE_NAME}")
    client: MongoClient = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["customers"]

    # Find existing admin by old email
    existing = collection.find_one({"auth.email": OLD_ADMIN_EMAIL})
    if not existing:
        # Try finding by new email (already updated)
        existing = collection.find_one({"auth.email": NEW_ADMIN_EMAIL})
        if existing:
            print(f"Admin email already updated to: {NEW_ADMIN_EMAIL}")
        else:
            print(f"ERROR: No admin found with email '{OLD_ADMIN_EMAIL}' or '{NEW_ADMIN_EMAIL}'.")
            print("Please check the database manually.")
            client.close()
            return

    doc_id = existing["_id"]
    pwd_hash = hash_password(NEW_ADMIN_PASSWORD)

    result = collection.update_one(
        {"_id": doc_id},
        {
            "$set": {
                "auth.email": NEW_ADMIN_EMAIL,
                "auth.password_hash": pwd_hash,
                "updated_at": datetime.now(UTC),
            }
        }
    )

    if result.modified_count > 0:
        print("SUCCESS: Admin credentials updated.")
        print(f"  Email    : {NEW_ADMIN_EMAIL}")
        print(f"  Password : {NEW_ADMIN_PASSWORD}")
    else:
        print("INFO: No changes made (already up to date).")

    client.close()


if __name__ == "__main__":
    run()
