from enum import Enum


class NotificationType(str, Enum):
    ORDER_CREATED = "order_created"
    PAYMENT_PROOF_SUBMITTED = "payment_proof_submitted"
    PAYMENT_APPROVED = "payment_approved"
    PAYMENT_REJECTED = "payment_rejected"
    ORDER_CONFIRMED = "order_confirmed"
    SHIPMENT_CREATED = "shipment_created"
    SHIPMENT_STATUS_UPDATED = "shipment_status_updated"
    LOW_STOCK_ALERT = "low_stock_alert"
