from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.models.shipment import Shipment, TimelineEvent
from app.repositories.order_repository import OrderRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.schemas.auth import TokenData
from app.services.audit_service import AuditService
from app.services.base import BaseService


class ShipmentService(BaseService[Shipment]):
    def __init__(
        self,
        repository: ShipmentRepository,
        order_repository: OrderRepository,
        audit_service: AuditService,
    ):
        super().__init__(repository)
        self.shipment_repository = repository
        self.order_repository = order_repository
        self.audit_service = audit_service

    async def create_shipment(
        self,
        order_id: str,
        carrier_name: str,
        tracking_number: str,
        awb_number: str,
        current_user: TokenData,
        ip_address: str | None = None,
    ) -> Shipment:
        """
        Creates a new manual shipment for a confirmed paid order.
        Verifies constraints (paid, confirmed, and no duplicate shipment).
        Appends initial pending timeline event.
        """
        # 1. Fetch order
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order '{order_id}' not found.")

        # 2. Validate order status constraints
        # Shipment can be created only for paid/confirmed orders
        if order.payment_status != "paid" or order.order_status != "confirmed":
            raise BaseAppException(
                message="Shipment can only be created for paid and confirmed orders.",
                code="ORDER_NOT_PAID_OR_CONFIRMED",
                status_code=400,
            )

        # 3. Prevent duplicate shipment for same order
        existing = await self.shipment_repository.get_by_order_id(order_id)
        if existing:
            raise BaseAppException(
                message=f"Shipment already exists for order '{order_id}'.",
                code="DUPLICATE_SHIPMENT",
                status_code=400,
            )

        # 4. Construct Shipment model
        initial_event = TimelineEvent(
            status="pending",
            message="Shipment details created manually.",
            timestamp=datetime.now(UTC),
            location=None,
        )

        new_shipment = Shipment(
            order_id=order_id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            carrier_name=carrier_name,
            tracking_number=tracking_number,
            awb_number=awb_number,
            status="pending",
            timeline=[initial_event],
        )

        shipment = await self.shipment_repository.insert(new_shipment)

        # 5. Log audit
        await self.audit_service.log_action(
            action="CREATE_SHIPMENT",
            target_collection="shipments",
            user_id=current_user.user_id,
            target_id=shipment.id,
            ip_address=ip_address,
        )

        return shipment

    async def update_shipment_status(
        self,
        shipment_id: str,
        status: str,
        message: str,
        location: str | None,
        current_user: TokenData,
        ip_address: str | None = None,
    ) -> Shipment:
        """
        Updates shipment status, appends timeline event, and updates order's fulfillment_status.
        """
        # 1. Fetch shipment
        shipment = await self.shipment_repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException(f"Shipment '{shipment_id}' not found.")

        # 2. Validate status value
        allowed_statuses = {
            "pending",
            "packed",
            "shipped",
            "out_for_delivery",
            "delivered",
            "failed",
            "returned",
        }
        if status not in allowed_statuses:
            raise BaseAppException(
                message=f"Invalid shipment status: '{status}'.",
                code="INVALID_SHIPMENT_STATUS",
                status_code=400,
            )

        # 3. Form new event & update arrays
        now = datetime.now(UTC)
        new_event = TimelineEvent(
            status=status,
            message=message,
            timestamp=now,
            location=location,
        )

        update_payload: dict[str, Any] = {
            "status": status,
            "updated_at": now,
        }

        # Handle specific timestamp updates
        if status == "shipped" and not shipment.shipped_at:
            update_payload["shipped_at"] = now
        elif status == "delivered" and not shipment.delivered_at:
            update_payload["delivered_at"] = now

        current_timeline = list(shipment.timeline)
        current_timeline.append(new_event)
        update_payload["timeline"] = [e.model_dump() for e in current_timeline]

        updated = await self.shipment_repository.update(shipment_id, update_payload)
        if not updated:
            raise BaseAppException("Failed to update shipment status.")

        # 4. Sync order fulfillment_status
        # Packed shipment should update order fulfillment_status=packed.
        # Shipped shipment should update order fulfillment_status=shipped.
        # Delivered shipment should update order fulfillment_status=delivered.
        if status in ("packed", "shipped", "delivered"):
            order_update = {
                "fulfillment_status": status,
                "updated_at": now,
            }
            await self.order_repository.update(shipment.order_id, order_update)

        # 5. Log audit
        await self.audit_service.log_action(
            action="UPDATE_SHIPMENT_STATUS",
            target_collection="shipments",
            user_id=current_user.user_id,
            target_id=shipment_id,
            ip_address=ip_address,
        )

        return updated

    async def get_shipment_by_id(
        self,
        shipment_id: str,
        current_user: TokenData,
    ) -> Shipment:
        """
        Retrieves a shipment by ID. Customers can only view their own shipments.
        """
        shipment = await self.shipment_repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException(f"Shipment '{shipment_id}' not found.")

        # Authorization check
        from app.core.roles import UserRole, get_role_permissions
        permissions = get_role_permissions(current_user.role)
        is_staff = UserRole.ADMIN in permissions or UserRole.WAREHOUSE in permissions

        if not is_staff and shipment.customer_id != current_user.user_id:
            raise PermissionDeniedException("Access forbidden to this shipment.")

        return shipment

    async def get_shipment_by_order_id(
        self,
        order_id: str,
        current_user: TokenData,
    ) -> Shipment:
        """
        Retrieves a shipment by associated order ID. Customers can only view their own shipments.
        """
        shipment = await self.shipment_repository.get_by_order_id(order_id)
        if not shipment:
            raise NotFoundException(f"Shipment for order '{order_id}' not found.")

        # Authorization check
        from app.core.roles import UserRole, get_role_permissions
        permissions = get_role_permissions(current_user.role)
        is_staff = UserRole.ADMIN in permissions or UserRole.WAREHOUSE in permissions

        if not is_staff and shipment.customer_id != current_user.user_id:
            raise PermissionDeniedException("Access forbidden to this shipment.")

        return shipment

    async def get_all_shipments(self, skip: int = 0, limit: int = 100) -> list[Shipment]:
        """
        Retrieves all shipments (paginated).
        """
        return await self.shipment_repository.find({}, skip=skip, limit=limit)

    def map_to_response(self, shipment: Shipment) -> dict[str, Any]:
        """
        Converts a Shipment instance attributes to a standard response dictionary.
        """
        return {
            "id": shipment.id,
            "order_id": shipment.order_id,
            "order_number": shipment.order_number,
            "customer_id": shipment.customer_id,
            "carrier_name": shipment.carrier_name,
            "tracking_number": shipment.tracking_number,
            "awb_number": shipment.awb_number,
            "status": shipment.status,
            "timeline": [
                {
                    "status": event.status,
                    "message": event.message,
                    "timestamp": event.timestamp,
                    "location": event.location,
                }
                for event in shipment.timeline
            ],
            "shipped_at": shipment.shipped_at,
            "delivered_at": shipment.delivered_at,
            "created_at": shipment.created_at,
            "updated_at": shipment.updated_at,
        }
