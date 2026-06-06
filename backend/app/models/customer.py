from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.core.roles import UserRole
from app.models.base import MongoBaseModel


class CustomerAuth(BaseModel):
    email: str | None = None
    phone: str
    password_hash: str | None = None
    status: str = "active"
    refresh_token_hash: str | None = None
    role: UserRole = UserRole.CUSTOMER

class PersonalDetails(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

class CustomerAddress(BaseModel):
    address_id: str
    name: str
    phone: str
    street: str
    landmark: str | None = None
    pincode: str
    city: str
    state: str
    is_default_shipping: bool = False
    is_default_billing: bool = False

class B2BProfile(BaseModel):
    gstin: str
    credit_limit: float = 0.0
    credit_balance: float = 0.0
    discount_tier: str = "none"

class Customer(MongoBaseModel):
    auth: CustomerAuth
    personal_details: PersonalDetails = Field(default_factory=PersonalDetails)
    addresses: list[CustomerAddress] = Field(default_factory=list)
    b2b_profile: B2BProfile | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
