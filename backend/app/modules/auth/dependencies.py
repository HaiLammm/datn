from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Callable

from app.core import security
from app.core.config import settings
from app.modules.users.models import User
from app.modules.auth.schemas import TokenPayload
from app.modules.users.services import UserService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

refresh_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/refresh-token"
)


async def get_current_user(
    token: str = Depends(reusable_oauth2),
    user_service: UserService = Depends(UserService),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_service.get_user_by_email(email=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_user_from_refresh_token(
    token: str = Depends(refresh_oauth2),
    user_service: UserService = Depends(UserService),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_service.get_user_by_email(email=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================================
# Role-Based Access Control (RBAC) Dependencies
# ============================================================================

def require_role(allowed_roles: List[str]):
    """
    Factory function to create role-based guard dependencies.
    
    Admin users bypass all role checks and can access any endpoint.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint.
        
    Returns:
        A FastAPI dependency that validates user role.
        
    Example:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(['admin']))):
            ...
    """
    async def role_guard(current_user: User = Depends(get_current_active_user)) -> User:
        # Admin bypasses all role checks
        if current_user.role == 'admin':
            return current_user
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_guard


# Pre-built role guard dependencies for common use cases
require_admin = require_role(['admin'])
require_job_seeker = require_role(['job_seeker', 'admin'])
require_recruiter = require_role(['recruiter', 'admin'])


# Simple in-memory rate limiter for CV uploads
# In production, this should be replaced with Redis or similar
_cv_upload_requests = defaultdict(list)


async def rate_limit_cv_upload(
    current_user: User = Depends(require_job_seeker),
) -> User:
    """
    Rate limit CV uploads to 5 per minute per user.
    This is a simple in-memory implementation for demonstration.
    In production, use Redis or a distributed cache.
    
    Note: This dependency also enforces job_seeker or admin role.
    """
    now = datetime.utcnow()
    user_requests = _cv_upload_requests[current_user.id]

    # Remove requests older than 1 minute
    user_requests[:] = [req_time for req_time in user_requests if now - req_time < timedelta(minutes=1)]

    # Check if user has exceeded the limit
    if len(user_requests) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many CV upload requests. Please wait before uploading another CV.",
        )

    # Add current request
    user_requests.append(now)

    return current_user
