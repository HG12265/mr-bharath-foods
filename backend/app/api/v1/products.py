from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.models.product import Product, ProductVariant
from app.repositories.audit_repository import AuditRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.product import (
    ProductAttributeSchema,
    ProductCreate,
    ProductRatingsSchema,
    ProductResponse,
    ProductStatusUpdate,
    ProductUpdate,
    ProductVariantResponse,
    SEOMetadataSchema,
    SourcingDetailsSchema,
)
from app.services.audit_service import AuditService
from app.services.product_service import ProductService

router = APIRouter()


def get_product_service(db: AsyncDatabase = Depends(get_db)) -> ProductService:  # type: ignore[type-arg]
    repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    media_repo = MediaRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return ProductService(repo, category_repo, media_repo, audit_service)


def map_variant_response(var: ProductVariant) -> ProductVariantResponse:
    return ProductVariantResponse(
        variant_id=var.variant_id,
        sku=var.sku,
        title=var.title,
        volume_weight=var.volume_weight,
        price=var.price,
        stock_status=var.stock_status,
        is_active=var.is_active
    )


def map_product_response(prod: Product) -> ProductResponse:
    return ProductResponse(
        id=prod.id or "",
        name=prod.name,
        slug=prod.slug,
        description=prod.description,
        short_description=prod.short_description,
        category_id=prod.category_id,
        media_ids=prod.media_ids,
        sourcing=SourcingDetailsSchema(
            region=prod.sourcing.region,
            story=prod.sourcing.story,
            manufacturer_id=prod.sourcing.manufacturer_id
        ),
        attributes=[
            ProductAttributeSchema(name=attr.name, value=attr.value)
            for attr in prod.attributes
        ],
        variants=[map_variant_response(v) for v in prod.variants],
        seo=SEOMetadataSchema(
            meta_title=prod.seo.meta_title,
            meta_description=prod.seo.meta_description,
            meta_keywords=prod.seo.meta_keywords
        ),
        ratings=ProductRatingsSchema(
            average_rating=prod.ratings.average_rating,
            review_count=prod.ratings.review_count,
            total_reviews=prod.ratings.total_reviews,
            star_1_count=prod.ratings.star_1_count,
            star_2_count=prod.ratings.star_2_count,
            star_3_count=prod.ratings.star_3_count,
            star_4_count=prod.ratings.star_4_count,
            star_5_count=prod.ratings.star_5_count
        ),
        tags=prod.tags,
        search_keywords=prod.search_keywords,
        is_featured=prod.is_featured,
        status=prod.status,
        created_at=prod.created_at.isoformat(),
        updated_at=prod.updated_at.isoformat()
    )


# --- Public Endpoints ---

@router.get("", response_model=Envelope[list[ProductResponse]])
async def list_products(
    category_id: str | None = None,
    is_featured: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service)
) -> Envelope[list[ProductResponse]]:
    """
    Retrieves a list of active, non-deleted products. Supports category and featured filtering and pagination.
    """
    products = await service.list_public_products(
        category_id=category_id,
        is_featured=is_featured,
        skip=skip,
        limit=limit
    )
    return Envelope(
        success=True,
        message="Active products listed successfully.",
        data=[map_product_response(p) for p in products]
    )


@router.get("/admin/all", response_model=Envelope[list[ProductResponse]])
async def list_all_products_admin(
    category_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: ProductService = Depends(get_product_service)
) -> Envelope[list[ProductResponse]]:
    """
    Retrieves all products (active, draft, archived) for administration. Requires admin or warehouse role.
    """
    products = await service.list_all_products(
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    return Envelope(
        success=True,
        message="All products retrieved successfully for admin/warehouse.",
        data=[map_product_response(p) for p in products]
    )


@router.get("/{slug}", response_model=Envelope[ProductResponse])
async def get_product_by_slug(
    slug: str,
    service: ProductService = Depends(get_product_service)
) -> Envelope[ProductResponse]:
    """
    Retrieves details of an active, non-deleted product by slug.
    """
    product = await service.get_product_by_slug(slug)
    return Envelope(
        success=True,
        message="Product details retrieved successfully.",
        data=map_product_response(product)
    )


# --- Admin Endpoints ---

@router.post("", response_model=Envelope[ProductResponse])
async def create_product(
    request: Request,
    payload: ProductCreate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ProductService = Depends(get_product_service),
    db: AsyncDatabase = Depends(get_db)
) -> Envelope[ProductResponse]:
    """
    Creates a new product catalog node. Requires admin role.
    """
    ip = request.client.host if request.client else None
    product = await service.create_product(
        user_id=current_user.user_id,
        is_admin=True,
        request=payload,
        ip_address=ip
    )

    # Auto-create inventory records
    from app.repositories.inventory_repository import InventoryRepository
    from app.schemas.inventory import InventoryCreate, WarehouseStockSchema
    from app.services.inventory_service import InventoryService

    inv_repo = InventoryRepository(db)
    inv_service = InventoryService(inv_repo, service.product_repository, service.audit_service, None)

    for variant in product.variants:
        inv_payload = InventoryCreate(
            sku=variant.sku,
            variant_id=variant.variant_id,
            product_id=product.id or "",
            warehouse_stock=[WarehouseStockSchema(warehouse_id="WH-MAIN", on_hand=0, reserved=0)],
            safety_stock_level=10
        )
        try:
            await inv_service.create_inventory(inv_payload, ip_address=ip)
        except Exception:
            pass

    return Envelope(
        success=True,
        message="Product catalog listing registered successfully.",
        data=map_product_response(product)
    )


@router.patch("/{id}", response_model=Envelope[ProductResponse])
async def update_product(
    request: Request,
    id: str,
    payload: ProductUpdate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ProductService = Depends(get_product_service),
    db: AsyncDatabase = Depends(get_db)
) -> Envelope[ProductResponse]:
    """
    Modifies product catalog attributes. Requires admin role.
    """
    ip = request.client.host if request.client else None
    product = await service.update_product(
        user_id=current_user.user_id,
        is_admin=True,
        product_id=id,
        request=payload,
        ip_address=ip
    )

    # Auto-create inventory records for any new variants
    from app.repositories.inventory_repository import InventoryRepository
    from app.schemas.inventory import InventoryCreate, WarehouseStockSchema
    from app.services.inventory_service import InventoryService

    inv_repo = InventoryRepository(db)
    inv_service = InventoryService(inv_repo, service.product_repository, service.audit_service, None)

    for variant in product.variants:
        existing = await inv_repo.get_by_sku(variant.sku)
        if not existing:
            inv_payload = InventoryCreate(
                sku=variant.sku,
                variant_id=variant.variant_id,
                product_id=product.id or "",
                warehouse_stock=[WarehouseStockSchema(warehouse_id="WH-MAIN", on_hand=0, reserved=0)],
                safety_stock_level=10
            )
            try:
                await inv_service.create_inventory(inv_payload, ip_address=ip)
            except Exception:
                pass

    return Envelope(
        success=True,
        message="Product catalog parameters updated successfully.",
        data=map_product_response(product)
    )


@router.delete("/{id}", response_model=Envelope[None])
async def delete_product(
    request: Request,
    id: str,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ProductService = Depends(get_product_service)
) -> Envelope[None]:
    """
    Soft-deletes a product catalog listing. Requires admin role.
    """
    ip = request.client.host if request.client else None
    await service.delete_product(
        user_id=current_user.user_id,
        is_admin=True,
        product_id=id,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Product catalog listing soft-deleted successfully."
    )


@router.patch("/{id}/status", response_model=Envelope[ProductResponse])
async def update_product_status(
    request: Request,
    id: str,
    payload: ProductStatusUpdate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: ProductService = Depends(get_product_service)
) -> Envelope[ProductResponse]:
    """
    Updates activation status of a product (draft, active, archived). Requires admin role.
    """
    ip = request.client.host if request.client else None
    product = await service.update_product_status(
        user_id=current_user.user_id,
        is_admin=True,
        product_id=id,
        status=payload.status,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message=f"Product status revised to {payload.status} successfully.",
        data=map_product_response(product)
    )
