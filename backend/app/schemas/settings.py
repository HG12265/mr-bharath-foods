from decimal import Decimal

from pydantic import BaseModel, Field


class SettingsPublicResponse(BaseModel):
    tax_percentage: Decimal = Field(..., description="Tax percentage rate (e.g. 5.00 for 5%)")
    shipping_fee: Decimal = Field(..., description="Flat shipping fee amount")
    free_shipping_threshold: Decimal = Field(..., description="Free shipping order subtotal threshold")
    support_contact: str = Field(..., description="Customer support contact info")
    fssai_number: str | None = Field(default=None, description="FSSAI registration number")
    gst_number: str | None = Field(default=None, description="GST registration number")
    # Public-safe new fields
    brand_name: str | None = Field(default=None, description="Brand/business name")
    public_support_email: str | None = Field(default=None, description="Public support email address")
    public_support_phone: str | None = Field(default=None, description="Public support phone number")
    working_hours: str | None = Field(default=None, description="Storefront working hours")


class SettingsAdminResponse(BaseModel):
    id: str
    upi_id: str = Field(..., description="Merchant UPI ID deep link routing parameter")
    tax_percentage: Decimal
    shipping_fee: Decimal
    free_shipping_threshold: Decimal
    support_contact: str
    fssai_number: str | None
    gst_number: str | None
    # Business Identity
    brand_name: str | None
    support_email: str | None
    support_phone: str | None
    business_address: str | None
    # Payment Settings
    payment_display_name: str | None
    upi_instructions: str | None
    # Storefront Contact
    public_support_email: str | None
    public_support_phone: str | None
    working_hours: str | None


class SettingsUpdateSchema(BaseModel):
    upi_id: str | None = Field(default=None, description="Merchant UPI ID")
    tax_percentage: Decimal | None = Field(default=None, description="Tax rate percentage")
    shipping_fee: Decimal | None = Field(default=None, description="Flat shipping rate")
    free_shipping_threshold: Decimal | None = Field(default=None, description="Free shipping threshold")
    support_contact: str | None = Field(default=None, description="Support phone or email")
    fssai_number: str | None = Field(default=None, description="FSSAI registration number")
    gst_number: str | None = Field(default=None, description="GST registration number")
    # Business Identity
    brand_name: str | None = Field(default=None, description="Brand name")
    support_email: str | None = Field(default=None, description="Support email")
    support_phone: str | None = Field(default=None, description="Support phone number")
    business_address: str | None = Field(default=None, description="Business address")
    # Payment Settings
    payment_display_name: str | None = Field(default=None, description="Payment display name")
    upi_instructions: str | None = Field(default=None, description="Manual UPI instructions")
    # Storefront Contact
    public_support_email: str | None = Field(default=None, description="Public support email")
    public_support_phone: str | None = Field(default=None, description="Public support phone number")
    working_hours: str | None = Field(default=None, description="Working hours")

