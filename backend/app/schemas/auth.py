
from pydantic import BaseModel, Field

from app.core.roles import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole

class TokenData(BaseModel):
    user_id: str
    email: str | None = None
    role: UserRole

class OTPRequest(BaseModel):
    phone_number: str = Field(..., description="Indian phone number or international standard in E.164")
    email: str | None = Field(None, description="Optional user email coordinate")

class OTPVerify(BaseModel):
    phone_number: str
    otp_code: str = Field(..., min_length=4, max_length=6, description="Numerical verification code")

class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str | None = Field(None, description="Optional email address")
    phone_number: str = Field(..., description="E.164 format phone number")
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")

class LoginRequest(BaseModel):
    email_or_phone: str = Field(..., description="Username login email or phone number identifier")
    password: str = Field(..., description="Credentials password")

class PersonalDetailsResponse(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

class UserResponse(BaseModel):
    id: str
    email: str | None = None
    phone: str
    role: UserRole
    personal_details: PersonalDetailsResponse


class SessionResponse(BaseModel):
    authenticated: bool
    user: UserResponse | None = None


