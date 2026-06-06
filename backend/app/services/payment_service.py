from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.core.payment_rules import validate_payment_proof_file
from app.core.upi import generate_upi_link
from app.models.payment import Payment
from app.repositories.media_repository import MediaRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.auth import TokenData
from app.services.audit_service import AuditService
from app.services.base import BaseService


class PaymentService(BaseService[Payment]):
    def __init__(
        self,
        repository: PaymentRepository,
        order_repository: OrderRepository,
        media_repository: MediaRepository,
        audit_service: AuditService,
        notification_service: Any = None,
    ):
        super().__init__(repository)
        self.payment_repository = repository
        self.order_repository = order_repository
        self.media_repository = media_repository
        self.audit_service = audit_service
        self.notification_service = notification_service

    async def initiate_upi_payment(
        self,
        order_id: str,
        current_user: TokenData | None = None,
        guest_token: str | None = None,
        ip_address: str | None = None,
    ) -> Payment:
        """
        Initiates a manual UPI payment flow for an order.
        Verifies ownership and status constraints, generates the deep link, and upserts Payment record.
        """
        # 1. Fetch order
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order '{order_id}' not found.")

        # 2. Check ownership
        authorized = False
        if current_user:
            if order.customer_id == current_user.user_id:
                authorized = True
        else:
            if guest_token and order.guest_token == guest_token:
                authorized = True

        if not authorized:
            raise PermissionDeniedException("Access forbidden to this order.")

        # 3. Check order status constraints
        if order.payment_status == "paid":
            raise BaseAppException(
                message="Cannot pay for this order. It is already paid.",
                code="ORDER_ALREADY_PAID",
                status_code=400,
            )

        if order.order_status in ("cancelled", "closed"):
            raise BaseAppException(
                message=f"Cannot pay for this order. Status is '{order.order_status}'.",
                code="INVALID_ORDER_STATUS",
                status_code=400,
            )

        # 4. Check for existing payment
        existing = await self.payment_repository.get_by_order_id(order_id)
        if existing:
            if existing.status == "approved":
                raise BaseAppException(
                    message="Payment for this order is already approved.",
                    code="PAYMENT_ALREADY_APPROVED",
                    status_code=400,
                )
            if existing.status == "proof_submitted":
                return existing

        # 5. Generate link
        settings_doc = await self.payment_repository.db["settings"].find_one({"is_deleted": {"$ne": True}})
        upi_id = settings.UPI_ID
        if settings_doc and settings_doc.get("upi_id"):
            upi_id = settings_doc["upi_id"]

        upi_link = generate_upi_link(upi_id, order.pricing.grand_total, order.order_number)
        transaction_note = f"Order {order.order_number}"

        # 6. Save Payment
        if existing:
            # Re-initiate pending payment
            update_payload = {
                "status": "pending",
                "upi_id": upi_id,
                "upi_link": upi_link,
                "amount": order.pricing.grand_total,
                "transaction_note": transaction_note,
                "screenshot_media_id": None,
                "rejection_reason": None,
                "updated_at": datetime.now(UTC),
            }
            updated = await self.payment_repository.update(existing.id or "", update_payload)
            if not updated:
                raise BaseAppException("Failed to re-initiate payment record.")
            payment_record = updated
        else:
            new_payment = Payment(
                order_id=order_id,
                order_number=order.order_number,
                customer_id=order.customer_id,
                guest_token=order.guest_token,
                amount=order.pricing.grand_total,
                upi_id=upi_id,
                upi_link=upi_link,
                transaction_note=transaction_note,
                status="pending",
            )
            payment_record = await self.payment_repository.insert(new_payment)

        # Audit log
        operator = current_user.user_id if current_user else "guest"
        await self.audit_service.log_action(
            action="INITIATE_PAYMENT",
            target_collection="payments",
            user_id=operator,
            target_id=payment_record.id,
            ip_address=ip_address,
        )

        return payment_record

    async def submit_payment_proof(
        self,
        order_id: str,
        screenshot_media_id: str,
        current_user: TokenData | None = None,
        guest_token: str | None = None,
        ip_address: str | None = None,
    ) -> Payment:
        """
        Customer submits payment screenshot proof.
        Validates media file format, file size, status, and ownership constraints.
        """
        # 1. Fetch order & verify ownership
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order '{order_id}' not found.")

        authorized = False
        if current_user:
            if order.customer_id == current_user.user_id:
                authorized = True
        else:
            if guest_token and order.guest_token == guest_token:
                authorized = True

        if not authorized:
            raise PermissionDeniedException("Access forbidden to this order.")

        # 2. Fetch payment record
        payment = await self.payment_repository.get_by_order_id(order_id)
        if not payment:
            raise NotFoundException("Payment record not initiated for this order.")

        if payment.status == "approved":
            raise BaseAppException(
                message="Payment for this order is already approved.",
                code="PAYMENT_ALREADY_APPROVED",
                status_code=400,
            )

        # 3. Validate media proof
        media = await self.media_repository.get_by_id(screenshot_media_id)
        if not media:
            raise NotFoundException("Screenshot media asset not found.")

        if media.status != "completed":
            raise BaseAppException(
                message="Media upload has not completed.",
                code="INCOMPLETE_MEDIA",
                status_code=400,
            )

        if media.asset_type != "payment_proof":
            raise BaseAppException(
                message=f"Media asset must have asset_type = 'payment_proof', found '{media.asset_type}'.",
                code="INVALID_ASSET_TYPE",
                status_code=400,
            )

        # Validate format & size rules
        validate_payment_proof_file(media.content_type, media.size)

        # Validate media ownership
        media_owner_matched = False
        if current_user:
            if media.uploaded_by == current_user.user_id:
                media_owner_matched = True
        else:
            if guest_token and media.uploaded_by == guest_token:
                media_owner_matched = True

        if not media_owner_matched:
            raise PermissionDeniedException("Access forbidden: media proof uploaded by a different user.")

        # 4. Save Payment Proof submission
        update_payload = {
            "screenshot_media_id": screenshot_media_id,
            "status": "proof_submitted",
            "updated_at": datetime.now(UTC),
        }
        updated = await self.payment_repository.update(payment.id or "", update_payload)
        if not updated:
            raise BaseAppException("Failed to save payment proof details.")

        # Audit log
        operator = current_user.user_id if current_user else "guest"
        await self.audit_service.log_action(
            action="SUBMIT_PAYMENT_PROOF",
            target_collection="payments",
            user_id=operator,
            target_id=updated.id,
            ip_address=ip_address,
        )

        # Notification hook
        if self.notification_service:
            await self.notification_service.create_notification(
                type="payment_proof_submitted",
                title="Payment Proof Submitted",
                message=f"Payment proof submitted for order {order.order_number}.",
                role_target="warehouse",
                metadata={"order_id": order.id, "payment_id": updated.id},
                operator_id=operator,
                ip_address=ip_address,
            )

        return updated

    async def verify_payment_proof_admin(
        self,
        payment_id: str,
        action: str,
        rejection_reason: str | None,
        admin_user_id: str,
        ip_address: str | None = None,
    ) -> Payment:
        """
        Verifies or rejects payment proof (admin/warehouse role).
        If approved: sets order.payment_status = paid and order.order_status = confirmed.
        If rejected: sets order.payment_status = pending, order.order_status = pending_payment, and payment.status = rejected.
        """
        # 1. Fetch payment
        payment = await self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundException(f"Payment '{payment_id}' not found.")

        if payment.status != "proof_submitted":
            raise BaseAppException(
                message=f"No payment proof submitted to verify. Current status is '{payment.status}'.",
                code="PAYMENT_NOT_READY_FOR_VERIFICATION",
                status_code=400,
            )

        # 2. Fetch order
        order = await self.order_repository.get_by_id(payment.order_id)
        if not order:
            raise NotFoundException("Associated order not found.")

        # 3. Handle Verify Actions
        if action == "approve":
            # Update Payment status
            pay_update = {
                "status": "approved",
                "verified_by": admin_user_id,
                "verified_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
            updated_payment = await self.payment_repository.update(payment_id, pay_update)
            if not updated_payment:
                raise BaseAppException("Failed to update payment to approved.")

            # Update Order status
            order_update = {
                "payment_status": "paid",
                "order_status": "confirmed",
                "updated_at": datetime.now(UTC),
            }
            await self.order_repository.update(payment.order_id, order_update)

            # Audit log
            await self.audit_service.log_action(
                action="APPROVE_PAYMENT",
                target_collection="payments",
                user_id=admin_user_id,
                target_id=payment_id,
                ip_address=ip_address,
            )

            # Notification hooks
            if self.notification_service:
                await self.notification_service.create_notification(
                    type="payment_approved",
                    title="Payment Approved",
                    message=f"Your payment for order {order.order_number} has been approved.",
                    target_user_id=order.customer_id,
                    metadata={"order_id": order.id, "payment_id": payment_id},
                    operator_id=admin_user_id,
                    ip_address=ip_address,
                )
                await self.notification_service.create_notification(
                    type="order_confirmed",
                    title="Order Confirmed",
                    message=f"Your order {order.order_number} is now confirmed and paid.",
                    target_user_id=order.customer_id,
                    metadata={"order_id": order.id},
                    operator_id=admin_user_id,
                    ip_address=ip_address,
                )

            return updated_payment

        elif action == "reject":
            if not rejection_reason or not rejection_reason.strip():
                raise BaseAppException(
                    message="Rejection reason is required to reject a payment proof.",
                    code="REJECTION_REASON_REQUIRED",
                    status_code=400,
                )

            # Update Payment status
            pay_update = {
                "status": "rejected",
                "rejection_reason": rejection_reason.strip(),
                "verified_by": admin_user_id,
                "verified_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
            updated_payment = await self.payment_repository.update(payment_id, pay_update)
            if not updated_payment:
                raise BaseAppException("Failed to update payment to rejected.")

            # Update Order status
            order_update = {
                "payment_status": "pending",
                "order_status": "pending_payment",
                "updated_at": datetime.now(UTC),
            }
            await self.order_repository.update(payment.order_id, order_update)

            # Audit log
            await self.audit_service.log_action(
                action="REJECT_PAYMENT",
                target_collection="payments",
                user_id=admin_user_id,
                target_id=payment_id,
                ip_address=ip_address,
            )

            # Notification hook
            if self.notification_service:
                await self.notification_service.create_notification(
                    type="payment_rejected",
                    title="Payment Proof Rejected",
                    message=f"Your payment proof for order {order.order_number} was rejected. Reason: {rejection_reason}",
                    target_user_id=order.customer_id,
                    metadata={"order_id": order.id, "payment_id": payment_id},
                    operator_id=admin_user_id,
                    ip_address=ip_address,
                )

            return updated_payment

        else:
            raise BaseAppException(
                message=f"Invalid action '{action}'. Mode must be 'approve' or 'reject'.",
                code="INVALID_VERIFICATION_ACTION",
                status_code=400,
            )

    def map_to_response(self, payment: Payment) -> dict[str, Any]:
        """
        Maps Payment model instance attributes to a standard response dictionary.
        """
        return {
            "id": payment.id,
            "order_id": payment.order_id,
            "order_number": payment.order_number,
            "customer_id": payment.customer_id,
            "guest_token": payment.guest_token,
            "amount": payment.amount,
            "upi_id": payment.upi_id,
            "upi_link": payment.upi_link,
            "status": payment.status,
            "screenshot_media_id": payment.screenshot_media_id,
            "transaction_note": payment.transaction_note,
            "rejection_reason": payment.rejection_reason,
            "verified_by": payment.verified_by,
            "verified_at": payment.verified_at,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at,
        }
