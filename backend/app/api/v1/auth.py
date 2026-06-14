import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request, Response, status
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_current_user, get_db, get_optional_user, get_redis
from app.core.exceptions import AuthenticationException
from app.core.rate_limit import check_rate_limit
from app.repositories.customer_repository import CustomerRepository
from app.schemas.auth import (
    LoginRequest,
    OTPRequest,
    OTPVerify,
    PersonalDetailsResponse,
    RegisterRequest,
    SessionResponse,
    Token,
    TokenData,
    UserResponse,
)
from app.schemas.common import Envelope
from app.services.auth_service import AuthService

router = APIRouter()

def get_auth_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
    redis: aioredis.Redis = Depends(get_redis)
) -> AuthService:
    repo = CustomerRepository(db)
    return AuthService(repo, redis)

@router.post("/register", response_model=Envelope[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[UserResponse]:
    # Check general rate limits for register requests
    await check_rate_limit(request, key_prefix="rate_register", limit=5, window_seconds=600)

    customer = await service.register_customer(payload)

    user_data = UserResponse(
        id=customer.id or "",
        email=customer.auth.email,
        phone=customer.auth.phone,
        role=customer.auth.role,
        personal_details=PersonalDetailsResponse(
            first_name=customer.personal_details.first_name,
            last_name=customer.personal_details.last_name
        )
    )
    return Envelope(
        success=True,
        message="User account registered successfully.",
        data=user_data
    )

@router.post("/login", response_model=Envelope[Token])
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[Token]:
    # Limit login requests to prevent brute force (e.g. 5 requests per 10 mins)
    await check_rate_limit(request, key_prefix="rate_login", limit=5, window_seconds=600)

    customer = await service.authenticate_password(payload.email_or_phone, payload.password)
    access_token, refresh_token = service.create_tokens(customer)

    await service.save_refresh_token_hash(customer, refresh_token)

    # Secure HTTPOnly cookies mapping
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60,  # 30 days duration
    )

    token_data = Token(
        access_token=access_token,
        role=customer.auth.role
    )
    return Envelope(
        success=True,
        message="Authentication completed successfully.",
        data=token_data
    )

@router.post("/otp/request", response_model=Envelope[None])
async def request_otp(
    request: Request,
    payload: OTPRequest,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[None]:
    # Limit OTP generation (e.g. 5 requests per 10 minutes)
    await check_rate_limit(request, key_prefix="rate_otp_req", limit=5, window_seconds=600)

    otp_code = await service.generate_otp(payload.phone_number)

    # In production, dispatch otp_code via SMS/WhatsApp/Email client wrapper here.
    # We log the generated OTP for local testing purposes.
    from app.core.logging import logger
    logger.info(f"OTP Generation requested for {payload.phone_number}: Code => {otp_code}")

    return Envelope(
        success=True,
        message="Verification code dispatched successfully."
    )

@router.post("/otp/verify", response_model=Envelope[Token])
async def verify_otp(
    request: Request,
    response: Response,
    payload: OTPVerify,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[Token]:
    # Limit OTP verification checking attempts
    await check_rate_limit(request, key_prefix="rate_otp_verify", limit=5, window_seconds=600)

    customer = await service.verify_otp(payload.phone_number, payload.otp_code)
    access_token, refresh_token = service.create_tokens(customer)

    await service.save_refresh_token_hash(customer, refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60,
    )

    token_data = Token(
        access_token=access_token,
        role=customer.auth.role
    )
    return Envelope(
        success=True,
        message="Phone validation verified. Login credentials established.",
        data=token_data
    )

@router.post("/refresh", response_model=Envelope[Token])
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[Token]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AuthenticationException("Refresh token missing.")

    customer, access_token, new_refresh_token = await service.rotate_refresh_token(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60,
    )

    token_data = Token(
        access_token=access_token,
        role=customer.auth.role
    )
    return Envelope(
        success=True,
        message="Session credentials updated.",
        data=token_data
    )

@router.post("/logout", response_model=Envelope[None])
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
) -> Envelope[None]:
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    # Revoke session in DB
    # Fetch user if token header is present
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            exp = payload.get("exp")
            if user_id:
                customer = await service.repository.get_by_id(user_id)
                if customer:
                    await service.revoke_user_session(customer)
            if exp:
                await service.blacklist_access_token(token, int(exp))
        except Exception:
            # Silence token decoding failures on logout
            pass

    return Envelope(
        success=True,
        message="Session logged out successfully."
    )

@router.get("/session", response_model=Envelope[SessionResponse])
async def get_session_info(
    db: AsyncDatabase = Depends(get_db),          # type: ignore[type-arg]
    current_user: TokenData | None = Depends(get_optional_user)
) -> Envelope[SessionResponse]:
    if not current_user:
        return Envelope(
            success=True,
            message="Guest session retrieved.",
            data=SessionResponse(authenticated=False, user=None)
        )

    repo = CustomerRepository(db)
    customer = await repo.get_by_id(current_user.user_id)
    if not customer:
        return Envelope(
            success=True,
            message="Guest session retrieved.",
            data=SessionResponse(authenticated=False, user=None)
        )

    user_data = UserResponse(
        id=customer.id or "",
        email=customer.auth.email,
        phone=customer.auth.phone,
        role=customer.auth.role,
        personal_details=PersonalDetailsResponse(
            first_name=customer.personal_details.first_name,
            last_name=customer.personal_details.last_name
        )
    )
    return Envelope(
        success=True,
        message="Authenticated session retrieved.",
        data=SessionResponse(authenticated=True, user=user_data)
    )

@router.get("/me", response_model=Envelope[UserResponse])
async def get_current_user_profile(
    db: AsyncDatabase = Depends(get_db),          # type: ignore[type-arg]
    current_user: TokenData = Depends(get_current_user)
) -> Envelope[UserResponse]:
    repo = CustomerRepository(db)
    customer = await repo.get_by_id(current_user.user_id)
    if not customer:
        raise AuthenticationException("User profile not found.")

    user_data = UserResponse(
        id=customer.id or "",
        email=customer.auth.email,
        phone=customer.auth.phone,
        role=customer.auth.role,
        personal_details=PersonalDetailsResponse(
            first_name=customer.personal_details.first_name,
            last_name=customer.personal_details.last_name
        )
    )
    return Envelope(
        success=True,
        message="User profile retrieved successfully.",
        data=user_data
    )
