"""Authentication utilities."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    AUTH_ENABLED,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"dk_{secrets.token_urlsafe(32)}"


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: AsyncSession = Depends(get_db),
):
    """Get the current authenticated user."""
    from core.models import APIKey, User

    if not AUTH_ENABLED:
        return None

    if api_key:
        result = await db.execute(
            select(APIKey).where(APIKey.key == api_key, APIKey.is_active.is_(True))
        )
        api_key_record = result.scalar_one_or_none()
        if api_key_record:
            user_result = await db.execute(
                select(User).where(User.id == api_key_record.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user and user.is_active:
                api_key_record.last_used_at = datetime.now(timezone.utc)
                await db.commit()
                return user

    if credentials:
        payload = decode_token(credentials.credentials)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(
                    select(User).where(User.id == int(user_id))
                )
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: AsyncSession = Depends(get_db),
):
    """Get the current user if authenticated, otherwise None."""
    from core.models import APIKey, User

    if not AUTH_ENABLED:
        return None

    if api_key:
        result = await db.execute(
            select(APIKey).where(APIKey.key == api_key, APIKey.is_active.is_(True))
        )
        api_key_record = result.scalar_one_or_none()
        if api_key_record:
            user_result = await db.execute(
                select(User).where(User.id == api_key_record.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user and user.is_active:
                api_key_record.last_used_at = datetime.now(timezone.utc)
                await db.commit()
                return user

    if credentials:
        payload = decode_token(credentials.credentials)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(
                    select(User).where(User.id == int(user_id))
                )
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    return user

    return None


def require_auth(user=Depends(get_current_user)):
    """Dependency that requires authentication when AUTH_ENABLED is True."""
    if AUTH_ENABLED and user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user
