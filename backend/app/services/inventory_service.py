from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import BaseAppException, NotFoundException
from app.core.inventory_rules import (
    validate_adjustment_limit,
    validate_release_limit,
    validate_reservation_limit,
)
from app.core.warehouse_rules import validate_warehouse_id
from app.models.inventory import Inventory, WarehouseStock
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryCreate
from app.services.audit_service import AuditService
from app.services.base import BaseService


class InventoryService(BaseService[Inventory]):
    def __init__(
        self,
        repository: InventoryRepository,
        product_repository: ProductRepository,
        audit_service: AuditService,
    ):
        super().__init__(repository)
        self.inventory_repository = repository
        self.product_repository = product_repository
        self.audit_service = audit_service

    async def create_inventory(
        self, data: InventoryCreate, ip_address: str | None = None
    ) -> Inventory:
        """
        Creates a new inventory entry.
        Validates:
        - Product exists and is active.
        - Variant exists and variant SKU matches the provided SKU.
        - Inventory for this SKU does not already exist.
        - Warehouse IDs are valid format.
        """
        # 1. Validate product status
        product = await self.product_repository.get_by_id(data.product_id)
        if not product or product.is_deleted or product.status != "active":
            raise BaseAppException(
                message="Associated product does not exist, is inactive, or has been deleted.",
                code="INVALID_PRODUCT",
                status_code=400,
            )

        # 2. Validate variant status and SKU
        matching_variant = None
        for var in product.variants:
            if var.variant_id == data.variant_id:
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
                message="Specified product variant is inactive.",
                code="INACTIVE_VARIANT",
                status_code=400,
            )

        if matching_variant.sku != data.sku:
            raise BaseAppException(
                message=f"Variant SKU mismatch. Catalog has '{matching_variant.sku}' but got '{data.sku}'.",
                code="VARIANT_SKU_MISMATCH",
                status_code=400,
            )

        # 3. Prevent duplicate SKU records
        existing = await self.inventory_repository.get_by_sku(data.sku)
        if existing:
            raise BaseAppException(
                message=f"Inventory record for SKU '{data.sku}' already exists.",
                code="DUPLICATE_INVENTORY",
                status_code=400,
            )

        # 4. Validate warehouses
        for wh in data.warehouse_stock:
            validate_warehouse_id(wh.warehouse_id)

        # 5. Insert
        new_inventory = Inventory(
            sku=data.sku,
            variant_id=data.variant_id,
            product_id=data.product_id,
            warehouse_stock=[
                WarehouseStock(
                    warehouse_id=wh.warehouse_id,
                    on_hand=wh.on_hand,
                    reserved=wh.reserved,
                    location_code=wh.location_code,
                )
                for wh in data.warehouse_stock
            ],
            safety_stock_level=data.safety_stock_level,
        )

        inserted = await self.inventory_repository.insert(new_inventory)

        await self.audit_service.log_action(
            action="CREATE_INVENTORY",
            target_collection="inventories",
            user_id="system",  # will be overridden by caller principal in API
            target_id=inserted.id,
            ip_address=ip_address,
        )

        return inserted

    async def adjust_stock(
        self,
        sku: str,
        warehouse_id: str,
        quantity: int,
        location_code: str | None = None,
        ip_address: str | None = None,
        operator_id: str | None = None,
    ) -> Inventory:
        """
        Adjusts the physical on-hand quantity for a SKU in a warehouse.
        """
        validate_warehouse_id(warehouse_id)

        inventory = await self.inventory_repository.get_by_sku(sku)
        if not inventory:
            raise NotFoundException(f"Inventory record for SKU '{sku}' not found.")

        # Locate entry
        stock_list = list(inventory.warehouse_stock)
        target_entry = None
        for entry in stock_list:
            if entry.warehouse_id == warehouse_id:
                target_entry = entry
                break

        if target_entry:
            validate_adjustment_limit(target_entry.on_hand, quantity)
            target_entry.on_hand += quantity
            if location_code is not None:
                target_entry.location_code = location_code
        else:
            validate_adjustment_limit(0, quantity)
            new_entry = WarehouseStock(
                warehouse_id=warehouse_id,
                on_hand=quantity,
                reserved=0,
                location_code=location_code,
            )
            stock_list.append(new_entry)

        updated_payload = {
            "warehouse_stock": [item.model_dump() for item in stock_list],
            "updated_at": datetime.now(UTC),
        }

        updated = await self.inventory_repository.update(inventory.id or "", updated_payload)
        if not updated:
            raise BaseAppException("Failed to adjust inventory stock.")

        await self.audit_service.log_action(
            action="ADJUST_STOCK",
            target_collection="inventories",
            user_id=operator_id,
            target_id=inventory.id,
            ip_address=ip_address,
        )

        return updated

    async def reserve_stock(
        self,
        sku: str,
        warehouse_id: str,
        quantity: int,
        ip_address: str | None = None,
        operator_id: str | None = None,
    ) -> Inventory:
        """
        Reserves available stock for a variant SKU.
        Available = on_hand - reserved.
        """
        validate_warehouse_id(warehouse_id)

        inventory = await self.inventory_repository.get_by_sku(sku)
        if not inventory:
            raise NotFoundException(f"Inventory record for SKU '{sku}' not found.")

        stock_list = list(inventory.warehouse_stock)
        target_entry = None
        for entry in stock_list:
            if entry.warehouse_id == warehouse_id:
                target_entry = entry
                break

        if not target_entry:
            raise BaseAppException(
                message=f"No stock records exist for SKU '{sku}' in warehouse '{warehouse_id}'.",
                code="INSUFFICIENT_STOCK",
                status_code=400,
            )

        available = target_entry.on_hand - target_entry.reserved
        validate_reservation_limit(quantity, available)

        target_entry.reserved += quantity

        updated_payload = {
            "warehouse_stock": [item.model_dump() for item in stock_list],
            "updated_at": datetime.now(UTC),
        }

        updated = await self.inventory_repository.update(inventory.id or "", updated_payload)
        if not updated:
            raise BaseAppException("Failed to reserve stock.")

        await self.audit_service.log_action(
            action="RESERVE_STOCK",
            target_collection="inventories",
            user_id=operator_id,
            target_id=inventory.id,
            ip_address=ip_address,
        )

        return updated

    async def release_stock(
        self,
        sku: str,
        warehouse_id: str,
        quantity: int,
        ip_address: str | None = None,
        operator_id: str | None = None,
    ) -> Inventory:
        """
        Releases reserved stock (unlocks or cancels reservation).
        Decrements reserved.
        """
        validate_warehouse_id(warehouse_id)

        inventory = await self.inventory_repository.get_by_sku(sku)
        if not inventory:
            raise NotFoundException(f"Inventory record for SKU '{sku}' not found.")

        stock_list = list(inventory.warehouse_stock)
        target_entry = None
        for entry in stock_list:
            if entry.warehouse_id == warehouse_id:
                target_entry = entry
                break

        if not target_entry:
            raise BaseAppException(
                message=f"No stock records exist for SKU '{sku}' in warehouse '{warehouse_id}'.",
                code="RELEASE_LIMIT_EXCEEDED",
                status_code=400,
            )

        validate_release_limit(quantity, target_entry.reserved)

        target_entry.reserved -= quantity

        updated_payload = {
            "warehouse_stock": [item.model_dump() for item in stock_list],
            "updated_at": datetime.now(UTC),
        }

        updated = await self.inventory_repository.update(inventory.id or "", updated_payload)
        if not updated:
            raise BaseAppException("Failed to release stock.")

        await self.audit_service.log_action(
            action="RELEASE_STOCK",
            target_collection="inventories",
            user_id=operator_id,
            target_id=inventory.id,
            ip_address=ip_address,
        )

        return updated

    def get_inventory_summary(self, inventory: Inventory) -> dict[str, Any]:
        """
        Calculates and maps dynamic fields for the InventoryResponse schema.
        """
        on_hand_total = sum(wh.on_hand for wh in inventory.warehouse_stock)
        reserved_total = sum(wh.reserved for wh in inventory.warehouse_stock)
        available_total = on_hand_total - reserved_total
        is_low_stock = available_total < inventory.safety_stock_level

        return {
            "id": inventory.id,
            "sku": inventory.sku,
            "variant_id": inventory.variant_id,
            "product_id": inventory.product_id,
            "warehouse_stock": [
                {
                    "warehouse_id": wh.warehouse_id,
                    "on_hand": wh.on_hand,
                    "reserved": wh.reserved,
                    "location_code": wh.location_code,
                }
                for wh in inventory.warehouse_stock
            ],
            "safety_stock_level": inventory.safety_stock_level,
            "on_hand_total": on_hand_total,
            "reserved_total": reserved_total,
            "available_total": available_total,
            "is_low_stock": is_low_stock,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at,
        }

    async def list_low_stock_alerts_with_summaries(self) -> list[dict[str, Any]]:
        """
        Retrieves low stock alerts and compiles summaries.
        """
        alerts = await self.inventory_repository.get_low_stock_alerts()
        return [self.get_inventory_summary(item) for item in alerts]
