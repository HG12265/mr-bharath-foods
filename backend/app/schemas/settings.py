from decimal import Decimal

from pydantic import BaseModel, Field


class SettingsPublicResponse(BaseModel):
    tax_percentage: Decimal = Field(..., description="Tax percentage rate (e.g. 5.00 for 5%)")
    shipping_fee: Decimal = Field(..., description="Flat shipping fee amount")
    free_shipping_threshold: Decimal = Field(..., description="Free shipping order subtotal threshold")
    support_contact: str = Field(..., description="Customer support contact info")
    fssai_number: str | None = Field(default=None, description="FSSAI registration number")
    gst_number: str | None = Field(default=None, description="GST registration number")


class SettingsAdminResponse(BaseModel):
    id: str
    upi_id: str = Field(..., description="Merchant UPI ID deep link routing parameter")
    tax_percentage: Decimal
    shipping_fee: Decimal
    free_shipping_threshold: Decimal
    support_contact: str
    fssai_number: str | None
    gst_number: str | None


class SettingsUpdateSchema(BaseModel):
    upi_id: str | None = Field(default=None, description="Merchant UPI ID")
    tax_percentage: Decimal | None = Field(default=None, description="Tax rate percentage")
    shipping_fee: Decimal | None = Field(default=None, description="Flat shipping rate")
    free_shipping_threshold: Decimal | None = Field(default=None, description="Free shipping threshold")
    support_contact: str | None = Field(default=None, description="Support phone or email")
    fssai_number: str | None = Field(default=None, description="FSSAI registration number")
    gst_number: str | None = Field(default=None, description="GST registration number")
