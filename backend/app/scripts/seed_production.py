import asyncio
import os

from app.core.database import db_manager
from app.core.roles import UserRole
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.customer import Customer, CustomerAuth, PersonalDetails
from app.models.settings import Settings
from app.repositories.category_repository import CategoryRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.settings_repository import SettingsRepository


async def seed_production() -> None:
    print("Connecting to database...")
    await db_manager.connect_to_database()
    db = db_manager.db
    if db is None:
        raise RuntimeError("Database could not be initialized.")

    # 1. Seed Default Settings
    print("Seeding default settings...")
    settings_repo = SettingsRepository(db)
    existing_settings = await settings_repo.get_settings()
    if not existing_settings:
        from app.core.settings_defaults import DEFAULT_SETTINGS
        settings_doc = Settings.model_validate(DEFAULT_SETTINGS)
        await settings_repo.insert(settings_doc)
        print("Default settings document seeded successfully.")
    else:
        print("Settings already initialized. Skipping settings seeding.")

    # 2. Seed Initial Admin User
    print("Seeding default administrator...")
    customer_repo = CustomerRepository(db)
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bharathdelightfoods.in")
    admin_phone = os.getenv("ADMIN_PHONE", "9092748525")    
    admin_password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")

    existing_admin = await customer_repo.get_by_email_or_phone(admin_email)
    if not existing_admin:
        existing_admin = await customer_repo.get_by_email_or_phone(admin_phone)

    if not existing_admin:
        pwd_hash = get_password_hash(admin_password)
        new_admin = Customer(
            auth=CustomerAuth(
                email=admin_email,
                phone=admin_phone,
                password_hash=pwd_hash,
                status="active",
                role=UserRole.ADMIN,
            ),
            personal_details=PersonalDetails(
                first_name="System",
                last_name="Administrator",
            ),
        )
        await customer_repo.insert(new_admin)
        print(f"Admin user seeded successfully. Email: {admin_email}, Password: {admin_password}")
    else:
        print("Administrator already exists. Skipping admin seeding.")

    # 3. Seed Default Categories
    print("Seeding default categories...")
    category_repo = CategoryRepository(db)
    default_categories = [
        {"name": "Spices & Masalas", "slug": "spices-masalas", "description": "Authentic Indian pure ground spices and blends"},
        {"name": "Pure Honey", "slug": "pure-honey", "description": "100% natural, raw, and organic forest honey"},
        {"name": "Grains & Pulses", "slug": "grains-pulses", "description": "High-quality raw grains, rice varieties, and healthy pulses"},
        {"name": "Traditional Pickles", "slug": "traditional-pickles", "description": "Homemade recipes preserved traditionally"},
    ]

    for cat_data in default_categories:
        existing_cat = await category_repo.collection.find_one({"slug": cat_data["slug"], "is_deleted": {"$ne": True}})
        if not existing_cat:
            cat = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                level=0,
                is_active=True,
            )
            await category_repo.insert(cat)
            print(f"Category '{cat_data['name']}' seeded.")
        else:
            print(f"Category '{cat_data['name']}' already exists. Skipping.")

    await db_manager.close_database_connection()
    print("Seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_production())
