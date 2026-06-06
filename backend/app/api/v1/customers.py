from fastapi import APIRouter, Depends, Request, Response
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_current_user, get_db, require_role
from app.core.exceptions import BaseAppException
from app.core.roles import UserRole
from app.models.customer import Customer
from app.repositories.audit_repository import AuditRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.customer import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    CustomerProfileResponse,
    EmailUpdate,
    PersonalDetailsResponse,
    PhoneUpdate,
    ProfileUpdate,
    StatusUpdate,
)
from app.services.audit_service import AuditService
from app.services.customer_service import CustomerService

router = APIRouter()

def get_customer_service(
    db: AsyncDatabase = Depends(get_db)  # type: ignore[type-arg]
) -> CustomerService:
    repo = CustomerRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return CustomerService(repo, audit_service)

def map_profile_response(customer: Customer) -> CustomerProfileResponse:
    return CustomerProfileResponse(
        id=customer.id or "",
        email=customer.auth.email,
        phone=customer.auth.phone,
        role=customer.auth.role,
        status=customer.auth.status,
        personal_details=PersonalDetailsResponse(
            first_name=customer.personal_details.first_name,
            last_name=customer.personal_details.last_name,
            avatar_url=customer.personal_details.avatar_url
        ),
        addresses=[
            AddressResponse(
                address_id=addr.address_id,
                name=addr.name,
                phone=addr.phone,
                street=addr.street,
                landmark=addr.landmark,
                pincode=addr.pincode,
                city=addr.city,
                state=addr.state,
                is_default_shipping=addr.is_default_shipping,
                is_default_billing=addr.is_default_billing
            ) for addr in customer.addresses
        ],
        created_at=customer.created_at.isoformat()
    )

@router.get("/me", response_model=Envelope[CustomerProfileResponse])
async def get_my_profile(
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    customer = await service.get_profile(current_user.user_id)
    return Envelope(
        success=True,
        message="Customer profile retrieved successfully.",
        data=map_profile_response(customer)
    )

@router.patch("/me", response_model=Envelope[CustomerProfileResponse])
async def update_my_profile(
    request: Request,
    payload: ProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.update_profile(current_user.user_id, payload, ip_address=ip)
    return Envelope(
        success=True,
        message="Profile details updated successfully.",
        data=map_profile_response(customer)
    )

@router.post("/me/addresses", response_model=Envelope[CustomerProfileResponse])
async def add_my_address(
    request: Request,
    payload: AddressCreate,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.add_address(current_user.user_id, payload, ip_address=ip)
    return Envelope(
        success=True,
        message="Address registered successfully.",
        data=map_profile_response(customer)
    )

@router.put("/me/addresses/{address_id}", response_model=Envelope[CustomerProfileResponse])
async def update_my_address(
    request: Request,
    address_id: str,
    payload: AddressUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.update_address(current_user.user_id, address_id, payload, ip_address=ip)
    return Envelope(
        success=True,
        message="Address parameters updated successfully.",
        data=map_profile_response(customer)
    )

@router.delete("/me/addresses/{address_id}", response_model=Envelope[CustomerProfileResponse])
async def delete_my_address(
    request: Request,
    address_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.delete_address(current_user.user_id, address_id, ip_address=ip)
    return Envelope(
        success=True,
        message="Address deleted successfully.",
        data=map_profile_response(customer)
    )

@router.patch("/me/addresses/{address_id}/default", response_model=Envelope[CustomerProfileResponse])
async def set_my_default_address(
    request: Request,
    address_id: str,
    default_type: str = "both",  # values: shipping, billing, both
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.set_default_address(current_user.user_id, address_id, default_type, ip_address=ip)
    return Envelope(
        success=True,
        message=f"Address configured as default {default_type} coordinate successfully.",
        data=map_profile_response(customer)
    )

@router.patch("/me/email", response_model=Envelope[CustomerProfileResponse])
async def update_my_email(
    request: Request,
    payload: EmailUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.update_email(current_user.user_id, payload.email, ip_address=ip)
    return Envelope(
        success=True,
        message="Email coordinate updated successfully.",
        data=map_profile_response(customer)
    )

@router.patch("/me/phone", response_model=Envelope[CustomerProfileResponse])
async def update_my_phone(
    request: Request,
    payload: PhoneUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.update_phone(current_user.user_id, payload.phone, ip_address=ip)
    return Envelope(
        success=True,
        message="Phone coordinate updated successfully.",
        data=map_profile_response(customer)
    )

@router.delete("/me", response_model=Envelope[None])
async def deactivate_my_account(
    request: Request,
    response: Response,
    current_user: TokenData = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[None]:
    ip = request.client.host if request.client else None
    success = await service.soft_delete_customer(current_user.user_id, ip_address=ip)
    if not success:
        raise BaseAppException("Profile deactivation failed.")

    # Immediately revoke active credentials
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            exp = payload.get("exp")
            if exp:
                from app.core.database import db_manager
                if db_manager.db is None:
                    raise RuntimeError("Database pool not initialized")
                from app.repositories.customer_repository import CustomerRepository
                repo = CustomerRepository(db_manager.db)
                from app.core.redis import redis_manager
                from app.services.auth_service import AuthService
                if redis_manager.client:
                    auth_service = AuthService(repo, redis_manager.client)
                    await auth_service.blacklist_access_token(token, int(exp))
        except Exception:
            pass

    return Envelope(
        success=True,
        message="User profile deactivated and logged out successfully."
    )

@router.patch("/{id}/status", response_model=Envelope[CustomerProfileResponse])
async def admin_change_customer_status(
    request: Request,
    id: str,
    payload: StatusUpdate,
    admin_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CustomerService = Depends(get_customer_service)
) -> Envelope[CustomerProfileResponse]:
    ip = request.client.host if request.client else None
    customer = await service.update_customer_status(admin_user.user_id, id, payload.status, ip_address=ip)
    return Envelope(
        success=True,
        message=f"Customer status revised to {payload.status} successfully.",
        data=map_profile_response(customer)
    )
