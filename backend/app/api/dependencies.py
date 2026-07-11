from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_current_user(authorization: str | None = Header(None)) -> dict:
    """Extract and validate JWT from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.removeprefix("Bearer ")
    from app.security.authentication import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


def require_role(*allowed_roles: str):
    """Create a FastAPI dependency that checks the user has one of the allowed roles.

    Usage:
        @router.get("/endpoint", dependencies=[Depends(require_role("mp", "admin"))])
        async def handler(): ...
    """
    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {allowed_roles}",
            )
        return current_user
    return _check


# Pre-built role dependencies for common patterns
require_citizen = require_role("citizen")
require_mp = require_role("mp", "admin")
require_admin = require_role("admin")
require_officer = require_role("officer", "admin")
