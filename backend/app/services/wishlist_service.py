from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import BaseAppException, NotFoundException
from app.core.wishlist_rules import validate_wishlist_limit
from app.models.wishlist import Wishlist, WishlistItem
from app.repositories.product_repository import ProductRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService


class WishlistService(BaseService[Wishlist]):
    def __init__(
        self,
        repository: WishlistRepository,
        product_repository: ProductRepository,
        audit_service: AuditService,
    ):
        super().__init__(repository)
        self.wishlist_repository = repository
        self.product_repository = product_repository
        self.audit_service = audit_service

    async def get_or_create_wishlist(
        self, customer_id: str, ip_address: str | None = None
    ) -> Wishlist:
        """
        Retrieves the customer's wishlist, or creates it if it does not exist.
        """
        wishlist = await self.wishlist_repository.get_by_customer_id(customer_id)
        if not wishlist:
            new_wishlist = Wishlist(customer_id=customer_id, items=[])
            wishlist = await self.wishlist_repository.insert(new_wishlist)

            await self.audit_service.log_action(
                action="CREATE_WISHLIST",
                target_collection="wishlists",
                user_id=customer_id,
                target_id=wishlist.id,
                ip_address=ip_address,
            )
        return wishlist

    async def add_wishlist_item(
        self,
        customer_id: str,
        product_id: str,
        variant_id: str,
        ip_address: str | None = None,
    ) -> Wishlist:
        """
        Adds a product variant to the customer's wishlist.
        Validates:
        - Product exists, is active, and is not deleted.
        - Variant exists and is active.
        - Wishlist item count does not exceed limit.
        - Duplicate variant is not added.
        """
        wishlist = await self.get_or_create_wishlist(customer_id, ip_address=ip_address)

        # 1. Validate product status
        product = await self.product_repository.get_by_id(product_id)
        if not product or product.is_deleted or product.status != "active":
            raise BaseAppException(
                message="Associated product does not exist, is inactive, or has been deleted.",
                code="INVALID_PRODUCT",
                status_code=400,
            )

        # 2. Validate variant status
        matching_variant = None
        for var in product.variants:
            if var.variant_id == variant_id:
                matching_variant = var
                break

        if not matching_variant:
            raise BaseAppException(
                message="Specified variant does not exist within the product catalog.",
                code="INVALID_VARIANT",
                status_code=400,
            )

        if not matching_variant.is_active:
            raise BaseAppException(
                message="Specified product variant is inactive and cannot be wishlisted.",
                code="INACTIVE_VARIANT",
                status_code=400,
            )

        # 3. Validate wishlist limit
        validate_wishlist_limit(len(wishlist.items))

        # 4. Check for duplicates
        for item in wishlist.items:
            if item.variant_id == variant_id:
                raise BaseAppException(
                    message="This product variant is already in your wishlist.",
                    code="DUPLICATE_WISHLIST_ITEM",
                    status_code=400,
                )

        # 5. Append and persist
        new_item = WishlistItem(
            product_id=product_id,
            variant_id=variant_id,
            sku=matching_variant.sku,
            added_at=datetime.now(UTC),
        )

        wishlist.items.append(new_item)
        items_dump = [item.model_dump() for item in wishlist.items]

        updated = await self.wishlist_repository.update(
            wishlist.id or "", {"items": items_dump, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Failed to add variant to your wishlist.")

        await self.audit_service.log_action(
            action="ADD_WISHLIST_ITEM",
            target_collection="wishlists",
            user_id=customer_id,
            target_id=wishlist.id,
            ip_address=ip_address,
        )

        return updated

    async def remove_wishlist_item(
        self, customer_id: str, variant_id: str, ip_address: str | None = None
    ) -> Wishlist:
        """
        Removes a product variant from the customer's wishlist.
        """
        wishlist = await self.wishlist_repository.get_by_customer_id(customer_id)
        if not wishlist:
            raise NotFoundException("Wishlist not found for this customer.")

        item_found = False
        remaining_items = []
        for item in wishlist.items:
            if item.variant_id == variant_id:
                item_found = True
            else:
                remaining_items.append(item)

        if not item_found:
            raise NotFoundException("Product variant not found in your wishlist.")

        items_dump = [item.model_dump() for item in remaining_items]

        updated = await self.wishlist_repository.update(
            wishlist.id or "", {"items": items_dump, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Failed to remove variant from your wishlist.")

        await self.audit_service.log_action(
            action="REMOVE_WISHLIST_ITEM",
            target_collection="wishlists",
            user_id=customer_id,
            target_id=wishlist.id,
            ip_address=ip_address,
        )

        return updated

    async def list_wishlist_items_with_summaries(self, customer_id: str) -> list[dict[str, Any]]:
        """
        Lists wishlist items for the customer.
        Filters out items whose products or variants are deleted or inactive.
        """
        wishlist = await self.get_or_create_wishlist(customer_id)

        active_items = []
        for item in wishlist.items:
            product = await self.product_repository.get_by_id(item.product_id)
            if not product or product.is_deleted or product.status != "active":
                continue

            variant = None
            for var in product.variants:
                if var.variant_id == item.variant_id:
                    variant = var
                    break

            if not variant or not variant.is_active:
                continue

            summary = {
                "name": product.name,
                "slug": product.slug,
                "media_ids": product.media_ids,
                "price": variant.price,
                "sku": variant.sku,
                "stock_status": variant.stock_status,
            }

            active_items.append(
                {
                    "product_id": item.product_id,
                    "variant_id": item.variant_id,
                    "sku": item.sku,
                    "added_at": item.added_at.isoformat(),
                    "product_summary": summary,
                }
            )

        return active_items
