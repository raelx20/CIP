from functools import wraps
from typing import Callable

from fastapi import HTTPException, status

from app.domain.auth.value_objects import UserRole, ROLE_PERMISSIONS


def require_role(*roles: UserRole):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            user_role = UserRole(current_user.get("role"))
            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role: {[r.value for r in roles]}",
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_permission(user_role: UserRole, resource: str, action: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return any(
        p.resource == resource and p.action == action
        for p in permissions
    )
