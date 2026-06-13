from collections.abc import AsyncGenerator, Callable

import jwt
import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.database import db_manager
from app.core.exceptions import AuthenticationException, PermissionDeniedException
from app.core.redis import redis_manager
from app.core.roles import UserRole, get_role_permissions
from app.core.security import decode_access_token
from app.schemas.auth import TokenData

# HTTPBearer parser. Auto-error set to False to handle custom authentication exception structures
security_jwt = HTTPBearer(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncDatabase, None]:  # type: ignore[type-arg]
    """
    Yields the current active MongoDB database instance context.
    """
    if db_manager.db is None:
        raise RuntimeError("Database pool has not been initialized.")
    yield db_manager.db

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    Yields the current active Redis client context.
    """
    if redis_manager.client is None:
        raise RuntimeError("Redis connection pool has not been initialized.")
    yield redis_manager.client

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_jwt)
) -> TokenData:
    """
    Verifies JWT token signature and decodes user session claims.
    """
    if not credentials:
        raise AuthenticationException("Authorization headers missing.")

    try:
        # Check if access token is blacklisted in Redis
        if redis_manager.client:
            import hashlib
            token_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
            blacklisted = await redis_manager.client.get(f"blacklist:{token_hash}")
            if blacklisted:
                raise AuthenticationException("Token has been revoked.")

        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")
        role_str: str = payload.get("role", "customer")

        if not user_id:
            raise AuthenticationException("JWT claims signature invalid: missing subject.")

        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role_str)
        )
    except jwt.PyJWTError as exc:
        raise AuthenticationException(f"Token decoding failed: {exc!s}") from exc
    except ValueError as exc:
        raise AuthenticationException("Invalid user role mapping contained in credentials claims.") from exc

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_jwt)
) -> TokenData | None:
    """
    Decodes JWT token signature if provided, otherwise returns None.
    Does not raise AuthenticationException if credentials are missing or invalid,
    instead returning None to represent an anonymous session.
    """
    if not credentials:
        return None

    try:
        if redis_manager.client:
            import hashlib
            token_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
            blacklisted = await redis_manager.client.get(f"blacklist:{token_hash}")
            if blacklisted:
                return None

        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        email = payload.get("email")
        role_str = payload.get("role", "customer")

        if not user_id:
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role_str)
        )
    except Exception:
        return None

def require_role(required_role: UserRole) -> Callable[[TokenData], TokenData]:
    """
    Dependency checking user permissions clearance level.
    """
    def check_permissions(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        permissions = get_role_permissions(current_user.role)
        if required_role not in permissions:
            raise PermissionDeniedException(
                message=f"Insufficient clearance. Endpoint requires '{required_role.value}' clearance level."
            )
        return current_user
    return check_permissions
