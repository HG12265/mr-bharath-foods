from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

PaymentStatus = Literal["pending", "proof_submitted", "approved", "rejected"]


class PaymentInitiateResponse(BaseModel):
    payment_id: str
    order_id: str
    order_number: str
    amount: Decimal
    upi_id: str
    upi_link: str
    status: PaymentStatus


class PaymentProofSubmitRequest(BaseModel):
    screenshot_media_id: str


class PaymentProofSubmitResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    screenshot_media_id: str


class PaymentVerifyRequest(BaseModel):
    action: Literal["approve", "reject"]
    rejection_reason: str | None = None


class PaymentVerifyResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    order_status: str
    payment_status: str
