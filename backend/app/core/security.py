from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed value.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Computes a secure bcrypt hash of the given password.
    """
    # Truncate to 72 bytes to prevent any length exceptions in bcrypt
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(
    subject: str | Any,
    role: str,
    expires_delta: timedelta | None = None
) -> str:
    """
    Encodes claims into a signed HS256 JWT access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iat": datetime.now(UTC)
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates an incoming JWT token signature and expiration.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
