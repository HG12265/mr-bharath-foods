
from pydantic import BaseModel, Field

from app.core.roles import UserRole


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    avatar_url: str | None = Field(None, description="Direct URL matching uploaded avatar image in Cloudflare R2")

class AddressCreate(BaseModel):
    name: str = Field(..., description="Recipient name tag")
    phone: str = Field(..., description="Recipient contact phone number coordinates")
    street: str = Field(...)
    landmark: str | None = None
    pincode: str = Field(..., description="6-digit postal code standard")
    city: str = Field(...)
    state: str = Field(...)
    is_default_shipping: bool = False
    is_default_billing: bool = False

class AddressUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    street: str | None = None
    landmark: str | None = None
    pincode: str | None = None
    city: str | None = None
    state: str | None = None
    is_default_shipping: bool | None = None
    is_default_billing: bool | None = None

class EmailUpdate(BaseModel):
    email: str = Field(..., description="New email parameter update coordinate")

class PhoneUpdate(BaseModel):
    phone: str = Field(..., description="New E.164 phone parameter update coordinate")

class StatusUpdate(BaseModel):
    status: str = Field(..., description="Active, Suspended status mapping options")

class AddressResponse(BaseModel):
    address_id: str
    name: str
    phone: str
    street: str
    landmark: str | None = None
    pincode: str
    city: str
    state: str
    is_default_shipping: bool
    is_default_billing: bool

class PersonalDetailsResponse(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

class CustomerProfileResponse(BaseModel):
    id: str
    email: str | None = None
    phone: str
    role: UserRole
    status: str
    personal_details: PersonalDetailsResponse
    addresses: list[AddressResponse]
    created_at: str
