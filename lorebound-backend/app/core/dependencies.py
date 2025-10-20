"""FastAPI dependencies."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from ..repositories.base import get_session
from ..core.security import verify_token, extract_user_id_from_token
from ..domain.models import User
from ..domain.enums import UserStatus


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the JWT token
        payload = verify_token(credentials.credentials)
        user_id_str = payload.get("user_id")
        
        if user_id_str is None:
            raise credentials_exception
            
        user_id = UUID(user_id_str)
        
    except jwt.InvalidTokenError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """Get current user if token is provided, None otherwise."""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        user_id_str = payload.get("user_id")
        
        if user_id_str is None:
            return None
            
        user_id = UUID(user_id_str)
        
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
        
    except (jwt.InvalidTokenError, ValueError):
        return None
