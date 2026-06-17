import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.core.sku import validate_sku
from app.core.slug import slugify
from app.models.product import (
    Product,
    ProductAttribute,
    ProductRatings,
    ProductVariant,
    SEOMetadata,
    SourcingDetails,
)
from app.repositories.category_repository import CategoryRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.audit_service import AuditService
from app.services.base import BaseService


class ProductService(BaseService[Product]):
    def __init__(
        self,
        repository: ProductRepository,
        category_repository: CategoryRepository,
        media_repository: MediaRepository,
        audit_service: AuditService
    ):
        super().__init__(repository)
        self.product_repository = repository
        self.category_repository = category_repository
        self.media_repository = media_repository
        self.audit_service = audit_service

    async def get_product_by_slug(self, slug: str) -> Product:
        """
        Retrieves an active, non-deleted product by its slug.
        """
        product = await self.product_repository.get_by_slug(slug)
        if not product or product.is_deleted or product.status != "active":
            raise NotFoundException("Product not found or currently unavailable.")
        return product

    async def list_public_products(
        self,
        category_id: str | None = None,
        category_slug: str | None = None,
        search: str | None = None,
        sort: str | None = None,
        is_featured: bool | None = None,
        skip: int = 0,
        limit: int = 12
    ) -> tuple[list[Product], int]:
        """
        Retrieves active, non-deleted products with filters, search, sort, and pagination.
        """
        if category_slug and not category_id:
            category = await self.category_repository.get_by_slug(category_slug)
            if category:
                category_id = category.id
            else:
                return [], 0

        return await self.product_repository.get_active_products(
            category_id=category_id,
            search=search,
            sort=sort,
            is_featured=is_featured,
            skip=skip,
            limit=limit
        )

    async def list_all_products(
        self,
        category_id: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Product]:
        """
        Retrieves all non-deleted products (including drafts and archived).
        """
        return await self.product_repository.get_all_products(
            category_id=category_id,
            skip=skip,
            limit=limit
        )

    async def create_product(
        self,
        user_id: str,
        is_admin: bool,
        request: ProductCreate,
        ip_address: str | None = None
    ) -> Product:
        """
        Creates a new product with embedded variants. Requires administrative clearance.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to create products.")

        # Validate category_id
        category = await self.category_repository.get_by_id(request.category_id)
        if not category or category.is_deleted or not category.is_active:
            raise BaseAppException(
                message="Associated category does not exist, is inactive, or has been deleted.",
                code="INVALID_CATEGORY",
                status_code=400
            )

        # Validate media_ids
        for media_id in request.media_ids:
            media = await self.media_repository.get_by_id(media_id)
            if not media or media.is_deleted or media.status != "completed":
                raise BaseAppException(
                    message=f"Media asset '{media_id}' must be completed and not deleted.",
                    code="INVALID_MEDIA_ASSET",
                    status_code=400
                )

        # Determine and check slug uniqueness
        slug = request.slug.strip() if request.slug else slugify(request.name)
        if not slug:
            raise BaseAppException("Generated product slug is invalid.", code="INVALID_SLUG", status_code=400)

        existing_slug = await self.product_repository.get_by_slug(slug)
        if existing_slug:
            raise BaseAppException(
                message=f"Product slug '{slug}' is already in use.",
                code="DUPLICATE_SLUG",
                status_code=400
            )

        # Validate variant SKUs (local & global uniqueness checks)
        skus_seen = set()
        variants_to_create = []
        for variant in request.variants:
            sanitized_sku = validate_sku(variant.sku)
            if sanitized_sku in skus_seen:
                raise BaseAppException(
                    message=f"Duplicate SKU '{sanitized_sku}' contained in creation request.",
                    code="DUPLICATE_SKU",
                    status_code=400
                )
            skus_seen.add(sanitized_sku)

            # Check global SKU uniqueness in DB
            existing_sku = await self.product_repository.get_by_sku(sanitized_sku)
            if existing_sku:
                raise BaseAppException(
                    message=f"SKU '{sanitized_sku}' is already in use by another product.",
                    code="DUPLICATE_SKU",
                    status_code=400
                )

            variants_to_create.append(
                ProductVariant(
                    variant_id=str(uuid.uuid4()),
                    sku=sanitized_sku,
                    title=variant.title.strip(),
                    volume_weight=variant.volume_weight.strip(),
                    price=variant.price,
                    stock_status=variant.stock_status,
                    is_active=variant.is_active
                )
            )

        # Sourcing
        sourcing_details = SourcingDetails(
            region=request.sourcing.region.strip(),
            story=request.sourcing.story.strip(),
            manufacturer_id=request.sourcing.manufacturer_id
        )

        # SEO
        seo_meta = SEOMetadata()
        if request.seo:
            seo_meta = SEOMetadata(
                meta_title=request.seo.meta_title.strip() if request.seo.meta_title else None,
                meta_description=request.seo.meta_description.strip() if request.seo.meta_description else None,
                meta_keywords=request.seo.meta_keywords
            )

        # Attributes
        attributes_list = [
            ProductAttribute(name=attr.name.strip(), value=attr.value.strip())
            for attr in request.attributes
        ]

        from decimal import Decimal
        active_prices = [v.price for v in variants_to_create if v.is_active]
        min_price = min(active_prices) if active_prices else Decimal("0.0")

        new_product = Product(
            name=request.name.strip(),
            slug=slug,
            description=request.description.strip(),
            short_description=request.short_description.strip(),
            category_id=request.category_id,
            media_ids=request.media_ids,
            sourcing=sourcing_details,
            attributes=attributes_list,
            variants=variants_to_create,
            seo=seo_meta,
            ratings=ProductRatings(),
            tags=[t.strip() for t in request.tags] if request.tags else [],
            search_keywords=[k.strip() for k in request.search_keywords] if request.search_keywords else [],
            is_featured=request.is_featured,
            status=request.status,
            min_price=min_price,
            display_price=min_price
        )

        inserted = await self.product_repository.insert(new_product)

        await self.audit_service.log_action(
            action="CREATE_PRODUCT",
            target_collection="products",
            user_id=user_id,
            target_id=inserted.id,
            ip_address=ip_address
        )

        return inserted

    async def update_product(
        self,
        user_id: str,
        is_admin: bool,
        product_id: str,
        request: ProductUpdate,
        ip_address: str | None = None
    ) -> Product:
        """
        Updates product attributes and validates SKU/slug uniqueness constraints. Requires admin role.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to update products.")

        product = await self.product_repository.get_by_id(product_id)
        if not product or product.is_deleted:
            raise NotFoundException("Product not found.")

        update_data: dict[str, Any] = {"updated_at": datetime.now(UTC)}

        if request.name is not None:
            update_data["name"] = request.name.strip()

        # Update slug if specified
        if request.slug is not None:
            slug = request.slug.strip()
            if not slug:
                raise BaseAppException("Product slug cannot be empty.", code="INVALID_SLUG", status_code=400)
            existing = await self.product_repository.get_by_slug(slug)
            if existing and existing.id != product_id:
                raise BaseAppException(
                    message=f"Product slug '{slug}' is already in use by another product.",
                    code="DUPLICATE_SLUG",
                    status_code=400
                )
            update_data["slug"] = slug

        if request.description is not None:
            update_data["description"] = request.description.strip()

        if request.short_description is not None:
            update_data["short_description"] = request.short_description.strip()

        # Update category_id
        if request.category_id is not None:
            category = await self.category_repository.get_by_id(request.category_id)
            if not category or category.is_deleted or not category.is_active:
                raise BaseAppException(
                    message="Associated category does not exist, is inactive, or has been deleted.",
                    code="INVALID_CATEGORY",
                    status_code=400
                )
            update_data["category_id"] = request.category_id

        # Update media_ids
        if request.media_ids is not None:
            for media_id in request.media_ids:
                media = await self.media_repository.get_by_id(media_id)
                if not media or media.is_deleted or media.status != "completed":
                    raise BaseAppException(
                        message=f"Media asset '{media_id}' must be completed and not deleted.",
                        code="INVALID_MEDIA_ASSET",
                        status_code=400
                    )
            update_data["media_ids"] = request.media_ids

        # Sourcing
        if request.sourcing is not None:
            update_data["sourcing.region"] = request.sourcing.region.strip()
            update_data["sourcing.story"] = request.sourcing.story.strip()
            update_data["sourcing.manufacturer_id"] = request.sourcing.manufacturer_id

        # SEO
        if request.seo is not None:
            update_data["seo.meta_title"] = request.seo.meta_title.strip() if request.seo.meta_title else None
            update_data["seo.meta_description"] = request.seo.meta_description.strip() if request.seo.meta_description else None
            update_data["seo.meta_keywords"] = request.seo.meta_keywords

        # Attributes
        if request.attributes is not None:
            update_data["attributes"] = [
                {"name": attr.name.strip(), "value": attr.value.strip()}
                for attr in request.attributes
            ]

        # Variants
        if request.variants is not None:
            skus_seen = set()
            variants_to_update = []
            for variant in request.variants:
                sanitized_sku = validate_sku(variant.sku)
                if sanitized_sku in skus_seen:
                    raise BaseAppException(
                        message=f"Duplicate SKU '{sanitized_sku}' contained in update request.",
                        code="DUPLICATE_SKU",
                        status_code=400
                    )
                skus_seen.add(sanitized_sku)

                # Check SKU uniqueness globally (excluding current product's prior SKUs)
                existing_sku = await self.product_repository.get_by_sku(sanitized_sku)
                if existing_sku and existing_sku.id != product_id:
                    raise BaseAppException(
                        message=f"SKU '{sanitized_sku}' is already in use by another product.",
                        code="DUPLICATE_SKU",
                        status_code=400
                    )

                variants_to_update.append(
                    {
                        "variant_id": str(uuid.uuid4()),
                        "sku": sanitized_sku,
                        "title": variant.title.strip(),
                        "volume_weight": variant.volume_weight.strip(),
                        "price": variant.price,
                        "stock_status": variant.stock_status,
                        "is_active": variant.is_active
                    }
                )
            update_data["variants"] = variants_to_update
            from decimal import Decimal
            active_prices: list[Decimal] = [Decimal(str(v["price"])) for v in variants_to_update if v["is_active"]]
            min_price: Decimal = min(active_prices) if active_prices else Decimal("0.0")
            update_data["min_price"] = min_price
            update_data["display_price"] = min_price

        if request.tags is not None:
            update_data["tags"] = [t.strip() for t in request.tags]

        if request.search_keywords is not None:
            update_data["search_keywords"] = [k.strip() for k in request.search_keywords]

        if request.is_featured is not None:
            update_data["is_featured"] = request.is_featured

        if request.status is not None:
            if request.status not in ["draft", "active", "archived"]:
                raise BaseAppException("Invalid product status.", code="INVALID_STATUS", status_code=400)
            update_data["status"] = request.status

        updated = await self.product_repository.update(product_id, update_data)
        if not updated:
            raise BaseAppException("Failed to update product details.")

        await self.audit_service.log_action(
            action="UPDATE_PRODUCT",
            target_collection="products",
            user_id=user_id,
            target_id=product_id,
            ip_address=ip_address
        )

        return updated

    async def delete_product(
        self,
        user_id: str,
        is_admin: bool,
        product_id: str,
        ip_address: str | None = None
    ) -> bool:
        """
        Soft-deletes a product. Requires admin role.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to delete products.")

        product = await self.product_repository.get_by_id(product_id)
        if not product or product.is_deleted:
            raise NotFoundException("Product not found.")

        success = await self.product_repository.soft_delete(product_id)
        if not success:
            raise BaseAppException("Failed to delete product.")

        # Update deleted_at in db
        await self.product_repository.update(
            product_id,
            {"deleted_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}
        )

        await self.audit_service.log_action(
            action="DELETE_PRODUCT",
            target_collection="products",
            user_id=user_id,
            target_id=product_id,
            ip_address=ip_address
        )

        return True

    async def update_product_status(
        self,
        user_id: str,
        is_admin: bool,
        product_id: str,
        status: str,
        ip_address: str | None = None
    ) -> Product:
        """
        Revises the activation status of a product (draft, active, archived).
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to modify product status.")

        product = await self.product_repository.get_by_id(product_id)
        if not product or product.is_deleted:
            raise NotFoundException("Product not found.")

        if status not in ["draft", "active", "archived"]:
            raise BaseAppException("Invalid product status.", code="INVALID_STATUS", status_code=400)

        updated = await self.product_repository.update(
            product_id,
            {"status": status, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Failed to update product status.")

        await self.audit_service.log_action(
            action=f"UPDATE_PRODUCT_STATUS_{status.upper()}",
            target_collection="products",
            user_id=user_id,
            target_id=product_id,
            ip_address=ip_address
        )

        return updated
