from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from app.core.database import db_manager
from app.core.exceptions import BaseAppException
from app.services.audit_service import AuditService

router = APIRouter()


class ContactInquiryRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=200)
    phone: str = Field(..., min_length=10, max_length=15)
    inquiry_type: str = Field(..., min_length=1, max_length=80)
    message: str = Field(..., min_length=10, max_length=2000)


async def _send_contact_email_background(payload: ContactInquiryRequest) -> None:
    """Send contact inquiry email to admin in the background."""
    try:
        db = db_manager.db
        if db is None:
            return
        audit_service = AuditService(db)
        from app.services.email_service import EmailService
        email_service = EmailService(audit_service)
        await email_service.send_contact_inquiry_email(
            full_name=payload.full_name,
            customer_email=payload.email,
            phone=payload.phone,
            inquiry_type=payload.inquiry_type,
            message=payload.message,
        )
    except Exception:
        pass  # Background task — never crash the request


@router.post("/contact", tags=["Contact"])
async def submit_contact_inquiry(
    payload: ContactInquiryRequest,
    background_tasks: BackgroundTasks,
    request: Request,
) -> dict:
    """
    Public endpoint — submit a contact inquiry.
    Sends an email to admin (bharathdelightfoods@gmail.com) via Brevo.
    Always returns success to the user even if email fails (fire & forget).
    """
    if not payload.full_name.strip():
        raise BaseAppException(
            message="Full name cannot be empty.",
            code="VALIDATION_ERROR",
            status_code=422
        )
    background_tasks.add_task(_send_contact_email_background, payload)
    return {
        "success": True,
        "message": "Your inquiry has been received. We will get back to you within 24 hours."
    }
