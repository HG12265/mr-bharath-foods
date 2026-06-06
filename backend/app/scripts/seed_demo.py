import asyncio
from decimal import Decimal
from typing import Any

from bson import ObjectId

from app.core.database import db_manager
from app.models.inventory import Inventory, WarehouseStock
from app.models.product import Product, ProductVariant, SourcingDetails
from app.repositories.category_repository import CategoryRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository


async def seed_demo() -> None:
    print("Connecting to database...")
    await db_manager.connect_to_database()
    db = db_manager.db
    if db is None:
        raise RuntimeError("Database could not be initialized.")

    category_repo = CategoryRepository(db)
    product_repo = ProductRepository(db)
    inventory_repo = InventoryRepository(db)

    # Resolve category IDs by slug
    print("Resolving category IDs...")
    spices_cat = await category_repo.collection.find_one({"slug": "spices-masalas", "is_deleted": {"$ne": True}})
    honey_cat = await category_repo.collection.find_one({"slug": "pure-honey", "is_deleted": {"$ne": True}})
    grains_cat = await category_repo.collection.find_one({"slug": "grains-pulses", "is_deleted": {"$ne": True}})

    if not spices_cat or not honey_cat or not grains_cat:
        print("Required categories spices-masalas, pure-honey, or grains-pulses not found. Please run seed_production.py first.")
        await db_manager.close_database_connection()
        return

    spices_cat_id = str(spices_cat["_id"])
    honey_cat_id = str(honey_cat["_id"])
    grains_cat_id = str(grains_cat["_id"])

    # Sample Products Data
    sample_products: list[dict[str, Any]] = [
        {
            "name": "Kashmiri Chilli Powder",
            "slug": "kashmiri-chilli-powder",
            "description": "Premium quality sun-dried Kashmiri red chillies ground to a fine powder.",
            "short_description": "Sun-dried pure Kashmiri chilli powder",
            "category_id": spices_cat_id,
            "sourcing": SourcingDetails(region="Kashmir", story="Sourced directly from local farmers in the valleys of Kashmir."),
            "variants": [
                {
                    "variant_id": str(ObjectId()),
                    "sku": "KMS-CHILLI-250G",
                    "title": "250g Pack",
                    "volume_weight": "250g",
                    "price": Decimal("150.00"),
                },
                {
                    "variant_id": str(ObjectId()),
                    "sku": "KMS-CHILLI-500G",
                    "title": "500g Pack",
                    "volume_weight": "500g",
                    "price": Decimal("280.00"),
                },
            ],
        },
        {
            "name": "Raw Wild Forest Honey",
            "slug": "raw-wild-forest-honey",
            "description": "100% raw, organic, unfiltered honey collected from deep forest wild hives.",
            "short_description": "Raw organic forest honey",
            "category_id": honey_cat_id,
            "sourcing": SourcingDetails(region="Western Ghats", story="Harvested ethically by traditional tribal honey hunters."),
            "variants": [
                {
                    "variant_id": str(ObjectId()),
                    "sku": "RAW-HONEY-500G",
                    "title": "500g Jar",
                    "volume_weight": "500g",
                    "price": Decimal("350.00"),
                },
                {
                    "variant_id": str(ObjectId()),
                    "sku": "RAW-HONEY-1KG",
                    "title": "1kg Jar",
                    "volume_weight": "1kg",
                    "price": Decimal("650.00"),
                },
            ],
        },
        {
            "name": "Organic Ponni Boiled Rice",
            "slug": "organic-ponni-boiled-rice",
            "description": "Healthy organic ponni rice parboiled to retain rich nutrients and fiber.",
            "short_description": "Organic parboiled ponni rice",
            "category_id": grains_cat_id,
            "sourcing": SourcingDetails(region="Cauvery Delta", story="Grown using traditional natural farming methods without synthetic chemicals."),
            "variants": [
                {
                    "variant_id": str(ObjectId()),
                    "sku": "PONNI-RICE-5KG",
                    "title": "5kg Bag",
                    "volume_weight": "5kg",
                    "price": Decimal("420.00"),
                }
            ],
        },
    ]

    print("Seeding sample products...")
    for prod_data in sample_products:
        existing_prod = await product_repo.collection.find_one({"slug": prod_data["slug"], "is_deleted": {"$ne": True}})
        if not existing_prod:
            # Create variants list
            variants = []
            for v_data in prod_data["variants"]:
                variants.append(
                    ProductVariant(
                        variant_id=v_data["variant_id"],
                        sku=v_data["sku"],
                        title=v_data["title"],
                        volume_weight=v_data["volume_weight"],
                        price=v_data["price"],
                        stock_status="in_stock",
                        is_active=True,
                    )
                )

            prod = Product(
                name=prod_data["name"],
                slug=prod_data["slug"],
                description=prod_data["description"],
                short_description=prod_data["short_description"],
                category_id=prod_data["category_id"],
                sourcing=prod_data["sourcing"],
                variants=variants,
                status="active",
            )
            inserted_prod = await product_repo.insert(prod)
            print(f"Product '{prod_data['name']}' seeded successfully.")

            # Seed stock for each variant in inventories
            for variant in inserted_prod.variants:
                existing_inv = await inventory_repo.collection.find_one({"sku": variant.sku, "is_deleted": {"$ne": True}})
                if not existing_inv:
                    inv = Inventory(
                        sku=variant.sku,
                        product_id=inserted_prod.id or "",
                        variant_id=variant.variant_id,
                        warehouse_stock=[
                            WarehouseStock(warehouse_id="WH-MAIN", on_hand=100, reserved=0)
                        ],
                        safety_stock_level=10,
                    )
                    await inventory_repo.insert(inv)
                    print(f"Inventory stock seeded for variant SKU '{variant.sku}'.")
        else:
            print(f"Product '{prod_data['name']}' already exists. Skipping.")

    await db_manager.close_database_connection()
    print("Demo seeding completed.")


if __name__ == "__main__":
    asyncio.run(seed_demo())
