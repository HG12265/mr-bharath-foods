from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.cart_rules import validate_cart_size, validate_item_quantity
from app.core.cart_summary import calculate_cart_summary
from app.core.exceptions import BaseAppException, NotFoundException
from app.models.cart import Cart, CartItem
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService


class CartService(BaseService[Cart]):
    def __init__(
        self,
        repository: CartRepository,
        product_repository: ProductRepository,
        audit_service: AuditService,
    ):
        super().__init__(repository)
        self.cart_repository = repository
        self.product_repository = product_repository
        self.audit_service = audit_service

    async def get_or_create_cart(
        self,
        customer_id: str | None = None,
        guest_token: str | None = None,
        ip_address: str | None = None,
    ) -> Cart:
        """
        Retrieves the customer's or guest's active cart, or creates it if it does not exist.
        """
        if not customer_id and not guest_token:
            raise BaseAppException(
                message="Either customer_id or guest_token must be provided to fetch/create a cart.",
                code="BAD_REQUEST",
                status_code=400,
            )

        cart = None
        if customer_id:
            cart = await self.cart_repository.get_active_by_customer_id(customer_id)
        elif guest_token:
            cart = await self.cart_repository.get_active_by_guest_token(guest_token)

        if not cart:
            expires_at = None
            if not customer_id and guest_token:
                expires_at = datetime.now(UTC) + timedelta(days=14)

            new_cart = Cart(
                customer_id=customer_id,
                guest_token=guest_token,
                items=[],
                expires_at=expires_at,
                status="active",
            )
            cart = await self.cart_repository.insert(new_cart)

            await self.audit_service.log_action(
                action="CREATE_CART",
                target_collection="carts",
                user_id=customer_id or guest_token,
                target_id=cart.id,
                ip_address=ip_address,
            )

        return cart

    async def add_cart_item(
        self,
        customer_id: str | None = None,
        guest_token: str | None = None,
        product_id: str = "",
        variant_id: str = "",
        quantity: int = 1,
        ip_address: str | None = None,
    ) -> Cart:
        """
        Adds a product variant to the cart.
        Validates:
        - Product exists, is active, and is not deleted.
        - Variant exists and is active.
        - Cart unique rows limit is respected if adding a new item.
        - Increment quantity if duplicate, capped at 10.
        """
        cart = await self.get_or_create_cart(
            customer_id=customer_id, guest_token=guest_token, ip_address=ip_address
        )

        # 1. Validate quantity is at least 1
        validate_item_quantity(quantity)

        # 2. Validate product status
        product = await self.product_repository.get_by_id(product_id)
        if not product or product.is_deleted or product.status != "active":
            raise BaseAppException(
                message="Associated product does not exist, is inactive, or has been deleted.",
                code="INVALID_PRODUCT",
                status_code=400,
            )

        # 3. Validate variant status
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
                message="Specified product variant is inactive and cannot be added to cart.",
                code="INACTIVE_VARIANT",
                status_code=400,
            )

        # 4. Check duplicate and handle capping/limit
        item_found = False
        items_list = list(cart.items)
        for item in items_list:
            if item.variant_id == variant_id:
                item_found = True
                new_qty = item.quantity + quantity
                # Cap at max qty (10)
                item.quantity = min(new_qty, 10)
                item.updated_at = datetime.now(UTC)
                break

        if not item_found:
            # Check unique items limit
            validate_cart_size(len(items_list), is_new_item=True)
            # Create new cart item
            new_item = CartItem(
                product_id=product_id,
                variant_id=variant_id,
                sku=matching_variant.sku,
                quantity=min(quantity, 10),
                unit_price_snapshot=matching_variant.price,
                added_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            items_list.append(new_item)

        # 5. Prepare update payload
        update_payload: dict[str, Any] = {
            "items": [item.model_dump() for item in items_list],
            "updated_at": datetime.now(UTC),
        }
        if guest_token and not customer_id:
            update_payload["expires_at"] = datetime.now(UTC) + timedelta(days=14)

        updated_cart = await self.cart_repository.update(cart.id or "", update_payload)
        if not updated_cart:
            raise BaseAppException("Failed to add variant to your cart.")

        await self.audit_service.log_action(
            action="ADD_CART_ITEM",
            target_collection="carts",
            user_id=customer_id or guest_token,
            target_id=cart.id,
            ip_address=ip_address,
        )

        return updated_cart

    async def update_cart_item(
        self,
        customer_id: str | None = None,
        guest_token: str | None = None,
        variant_id: str = "",
        quantity: int = 1,
        ip_address: str | None = None,
    ) -> Cart:
        """
        Updates the quantity of a variant in the cart.
        """
        # 1. Retrieve cart
        cart = None
        if customer_id:
            cart = await self.cart_repository.get_active_by_customer_id(customer_id)
        elif guest_token:
            cart = await self.cart_repository.get_active_by_guest_token(guest_token)

        if not cart:
            raise NotFoundException("Cart not found.")

        # 2. Validate quantity limits
        validate_item_quantity(quantity)

        # 3. Locate item
        items_list = list(cart.items)
        item_found = False
        for item in items_list:
            if item.variant_id == variant_id:
                item_found = True
                item.quantity = quantity
                item.updated_at = datetime.now(UTC)
                break

        if not item_found:
            raise NotFoundException("Product variant not found in your cart.")

        # 4. Prepare update payload
        update_payload: dict[str, Any] = {
            "items": [item.model_dump() for item in items_list],
            "updated_at": datetime.now(UTC),
        }
        if guest_token and not customer_id:
            update_payload["expires_at"] = datetime.now(UTC) + timedelta(days=14)

        updated_cart = await self.cart_repository.update(cart.id or "", update_payload)
        if not updated_cart:
            raise BaseAppException("Failed to update cart item quantity.")

        await self.audit_service.log_action(
            action="UPDATE_CART_ITEM",
            target_collection="carts",
            user_id=customer_id or guest_token,
            target_id=cart.id,
            ip_address=ip_address,
        )

        return updated_cart

    async def remove_cart_item(
        self,
        customer_id: str | None = None,
        guest_token: str | None = None,
        variant_id: str = "",
        ip_address: str | None = None,
    ) -> Cart:
        """
        Removes a variant from the cart.
        """
        # 1. Retrieve cart
        cart = None
        if customer_id:
            cart = await self.cart_repository.get_active_by_customer_id(customer_id)
        elif guest_token:
            cart = await self.cart_repository.get_active_by_guest_token(guest_token)

        if not cart:
            raise NotFoundException("Cart not found.")

        # 2. Locate and remove item
        items_list = list(cart.items)
        item_found = False
        remaining_items = []
        for item in items_list:
            if item.variant_id == variant_id:
                item_found = True
            else:
                remaining_items.append(item)

        if not item_found:
            raise NotFoundException("Product variant not found in your cart.")

        # 3. Prepare update payload
        update_payload: dict[str, Any] = {
            "items": [item.model_dump() for item in remaining_items],
            "updated_at": datetime.now(UTC),
        }
        if guest_token and not customer_id:
            update_payload["expires_at"] = datetime.now(UTC) + timedelta(days=14)

        updated_cart = await self.cart_repository.update(cart.id or "", update_payload)
        if not updated_cart:
            raise BaseAppException("Failed to remove variant from your cart.")

        await self.audit_service.log_action(
            action="REMOVE_CART_ITEM",
            target_collection="carts",
            user_id=customer_id or guest_token,
            target_id=cart.id,
            ip_address=ip_address,
        )

        return updated_cart

    async def clear_cart(
        self,
        customer_id: str | None = None,
        guest_token: str | None = None,
        ip_address: str | None = None,
    ) -> Cart:
        """
        Clears all items in the cart.
        """
        # 1. Retrieve cart
        cart = None
        if customer_id:
            cart = await self.cart_repository.get_active_by_customer_id(customer_id)
        elif guest_token:
            cart = await self.cart_repository.get_active_by_guest_token(guest_token)

        if not cart:
            raise NotFoundException("Cart not found.")

        # 2. Prepare update payload
        update_payload: dict[str, Any] = {
            "items": [],
            "updated_at": datetime.now(UTC),
        }
        if guest_token and not customer_id:
            update_payload["expires_at"] = datetime.now(UTC) + timedelta(days=14)

        updated_cart = await self.cart_repository.update(cart.id or "", update_payload)
        if not updated_cart:
            raise BaseAppException("Failed to clear your cart.")

        await self.audit_service.log_action(
            action="CLEAR_CART",
            target_collection="carts",
            user_id=customer_id or guest_token,
            target_id=cart.id,
            ip_address=ip_address,
        )

        return updated_cart

    async def merge_carts(
        self, customer_id: str, guest_token: str, ip_address: str | None = None
    ) -> Cart:
        """
        Merges guest cart into customer cart after login.
        - Guest cart items are moved/merged to customer cart.
        - Capped at max quantity (10) per item.
        - Unique items limit (50) is validated.
        - Guest cart status is marked as "converted".
        """
        # 1. Retrieve/Create customer cart
        customer_cart = await self.get_or_create_cart(
            customer_id=customer_id, ip_address=ip_address
        )

        # 2. Retrieve guest cart
        guest_cart = await self.cart_repository.get_active_by_guest_token(guest_token)
        if not guest_cart or not guest_cart.items:
            return customer_cart

        # 3. Consolidate items
        customer_items = {item.variant_id: item for item in customer_cart.items}

        for guest_item in guest_cart.items:
            if guest_item.variant_id in customer_items:
                # Increment quantity, capped by max qty (10)
                existing_item = customer_items[guest_item.variant_id]
                existing_item.quantity = min(existing_item.quantity + guest_item.quantity, 10)
                existing_item.updated_at = datetime.now(UTC)
            else:
                # Check unique rows limit
                validate_cart_size(len(customer_items), is_new_item=True)
                new_item = guest_item.model_copy()
                new_item.added_at = datetime.now(UTC)
                new_item.updated_at = datetime.now(UTC)
                # Ensure the guest item quantity itself is within bounds
                new_item.quantity = min(new_item.quantity, 10)
                customer_items[new_item.variant_id] = new_item

        # 4. Save customer cart
        customer_cart.items = list(customer_items.values())
        customer_cart.updated_at = datetime.now(UTC)
        updated_customer_cart = await self.cart_repository.update(
            customer_cart.id or "",
            {
                "items": [item.model_dump() for item in customer_cart.items],
                "updated_at": customer_cart.updated_at,
            },
        )
        if not updated_customer_cart:
            raise BaseAppException("Failed to update customer cart during merge.")

        # 5. Mark guest cart as converted/merged
        await self.cart_repository.update(
            guest_cart.id or "",
            {"status": "converted", "expires_at": None, "updated_at": datetime.now(UTC)},
        )

        # 6. Audit log
        await self.audit_service.log_action(
            action="MERGE_CART",
            target_collection="carts",
            user_id=customer_id,
            target_id=customer_cart.id,
            ip_address=ip_address,
        )

        return updated_customer_cart

    async def get_cart_with_summaries(
        self, customer_id: str | None = None, guest_token: str | None = None
    ) -> dict[str, Any]:
        """
        Retrieves active cart and computes decimal-safe summaries with dynamic product data.
        Filters out inactive or soft-deleted products and inactive variants.
        """
        cart = await self.get_or_create_cart(customer_id=customer_id, guest_token=guest_token)

        active_items = []
        for item in cart.items:
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

            # Check if variant price changed or snapshots are fresh, we still use the snapshot or dynamic?
            # Requirement says: "Use Decimal-safe pricing and summaries."
            # "Return product summary data for cart listing."
            summary = {
                "name": product.name,
                "slug": product.slug,
                "media_ids": product.media_ids,
                "price": variant.price,  # use current live price for listing
                "sku": variant.sku,
                "stock_status": variant.stock_status,
            }

            active_items.append(
                {
                    "product_id": item.product_id,
                    "variant_id": item.variant_id,
                    "sku": item.sku,
                    "quantity": item.quantity,
                    "unit_price_snapshot": item.unit_price_snapshot,
                    "added_at": item.added_at,
                    "updated_at": item.updated_at,
                    "product_summary": summary,
                }
            )

        # Compute dynamic summary of active/filtered items
        summary_totals = calculate_cart_summary(active_items)

        return {
            "id": cart.id,
            "customer_id": cart.customer_id,
            "guest_token": cart.guest_token,
            "items": active_items,
            "summary": summary_totals,
            "status": cart.status,
            "expires_at": cart.expires_at,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
        }
