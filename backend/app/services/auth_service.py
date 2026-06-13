import hashlib
import random
from datetime import UTC, datetime, timedelta

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.roles import UserRole
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.customer import Customer, CustomerAuth, PersonalDetails
from app.repositories.customer_repository import CustomerRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, repository: CustomerRepository, redis: "aioredis.Redis"):
        self.repository = repository
        self.redis = redis

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def register_customer(self, request: RegisterRequest) -> Customer:
        # Check if customer already exists
        existing = await self.repository.get_by_email_or_phone(request.phone_number)
        if not existing and request.email:
            existing = await self.repository.get_by_email_or_phone(request.email)

        if existing:
            raise AuthenticationException("A user with this email or phone number is already registered.")

        # Hash password
        pwd_hash = get_password_hash(request.password)

        new_customer = Customer(
            auth=CustomerAuth(
                email=request.email,
                phone=request.phone_number,
                password_hash=pwd_hash,
                status="active",
                role=UserRole.CUSTOMER,
            ),
            personal_details=PersonalDetails(
                first_name=request.first_name,
                last_name=request.last_name,
            )
        )

        return await self.repository.insert(new_customer)

    async def authenticate_password(self, email_or_phone: str, password: str) -> Customer:
        customer = await self.repository.get_by_email_or_phone(email_or_phone)
        if not customer:
            raise AuthenticationException("Invalid credentials.")

        if not customer.auth.password_hash or not verify_password(password, customer.auth.password_hash):
            raise AuthenticationException("Invalid credentials.")

        if customer.auth.status != "active":
            raise AuthenticationException("User account is inactive or suspended.")

        return customer

    async def generate_otp(self, phone: str) -> str:
        # Generate 6-digit secure numeric code
        otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])

        # Store in Redis (5 minutes expiry)
        await self.redis.setex(f"otp:{phone}", 300, otp_code)
        await self.redis.setex(f"otp_attempts:{phone}", 300, "0")

        return otp_code

    async def verify_otp(self, phone: str, otp_code: str) -> Customer:
        attempts_str = await self.redis.get(f"otp_attempts:{phone}")
        if attempts_str is not None and int(attempts_str) >= 3:
            await self.redis.delete(f"otp:{phone}")
            raise AuthenticationException("OTP verification attempts limit exceeded. Please request a new OTP.")

        stored_otp = await self.redis.get(f"otp:{phone}")
        if not stored_otp:
            raise AuthenticationException("OTP has expired or does not exist.")

        if stored_otp != otp_code:
            await self.redis.incrby(f"otp_attempts:{phone}", 1)
            raise AuthenticationException("Invalid verification code.")

        # Success: clear OTP session
        await self.redis.delete(f"otp:{phone}")
        await self.redis.delete(f"otp_attempts:{phone}")

        # Fetch or create customer dynamically if not registered
        customer = await self.repository.get_by_phone(phone)
        if not customer:
            # Automatically register standard customer on first verified OTP (standard D2C signup)
            new_customer = Customer(
                auth=CustomerAuth(
                    phone=phone,
                    status="active",
                    role=UserRole.CUSTOMER,
                )
            )
            customer = await self.repository.insert(new_customer)

        if customer.auth.status != "active":
            raise AuthenticationException("User account is inactive or suspended.")

        return customer

    def create_tokens(self, customer: Customer) -> tuple[str, str]:
        # Short-lived access token
        access_token = create_access_token(
            subject=customer.id,
            role=customer.auth.role.value,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        # Long-lived refresh token
        refresh_token = create_access_token(
            subject=customer.id,
            role=customer.auth.role.value,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return access_token, refresh_token

    async def save_refresh_token_hash(self, customer: Customer, refresh_token: str) -> None:
        token_hash = self._hash_token(refresh_token)
        await self.repository.update(
            id_str=customer.id or "",
            update_data={"auth.refresh_token_hash": token_hash, "updated_at": datetime.now(UTC)}
        )

    async def blacklist_access_token(self, token: str, exp_timestamp: int) -> None:
        token_hash = self._hash_token(token)
        now_ts = int(datetime.now(UTC).timestamp())
        expires_in = max(exp_timestamp - now_ts, 1)
        await self.redis.setex(f"blacklist:{token_hash}", expires_in, "true")

    async def is_access_token_blacklisted(self, token: str) -> bool:
        token_hash = self._hash_token(token)
        val = await self.redis.get(f"blacklist:{token_hash}")
        return val is not None

    async def rotate_refresh_token(self, refresh_token: str) -> tuple[Customer, str, str]:
        try:
            from app.core.security import decode_access_token
            payload = decode_access_token(refresh_token)
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationException("Invalid token payload.")
        except Exception as exc:
            raise AuthenticationException("Invalid or expired refresh token.") from exc

        customer = await self.repository.get_by_id(user_id)
        if not customer or customer.auth.status != "active":
            raise AuthenticationException("User account inactive or not found.")

        token_hash = self._hash_token(refresh_token)
        if customer.auth.refresh_token_hash != token_hash:
            # Token reuse detected: clear all tokens for security
            await self.repository.update(
                id_str=customer.id or "",
                update_data={"auth.refresh_token_hash": None, "updated_at": datetime.now(UTC)}
            )
            raise AuthenticationException("Token reuse detected. Session revoked.")

        # Issue new pair
        access_token, new_refresh_token = self.create_tokens(customer)
        await self.save_refresh_token_hash(customer, new_refresh_token)

        return customer, access_token, new_refresh_token

    async def revoke_user_session(self, customer: Customer) -> None:
        await self.repository.update(
            id_str=customer.id or "",
            update_data={"auth.refresh_token_hash": None, "updated_at": datetime.now(UTC)}
        )
