"""User repository for database operations."""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from ..domain.models import User, Profile
from ..domain.enums import UserStatus

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        apple_sub: Optional[str] = None,
        status: UserStatus = UserStatus.ACTIVE
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            apple_sub=apple_sub,
            status=status
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_apple_sub(self, apple_sub: str) -> Optional[User]:
        """Get user by Apple subject ID."""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.apple_sub == apple_sub)
        )
        return result.scalar_one_or_none()

    async def update_user_login_time(self, user_id: UUID) -> bool:
        """Update user's last login time."""
        from datetime import datetime, timezone
        
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0

    async def update_user_status(self, user_id: UUID, status: UserStatus) -> bool:
        """Update user status."""
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(status=status)
        )
        return result.rowcount > 0

    async def add_experience(self, user_id: UUID, xp_amount: int, session: AsyncSession = None) -> bool:
        """Add experience points to user's profile."""
        # Get user's profile
        result = await self.session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return False
        
        # Add XP and check for level up
        profile.xp += xp_amount
        
        # Simple level up formula: Level = floor(XP / 1000) + 1
        new_level = (profile.xp // 1000) + 1
        if new_level > profile.level:
            profile.level = new_level
            logger.info(f"User {user_id} leveled up to {new_level}!")
        
        await self.session.flush()
        return True

    async def create_profile(
        self,
        user_id: UUID,
        handle: str,
        level: int = 1,
        xp: int = 0,
        avatar_layers: Optional[dict] = None
    ) -> Profile:
        """Create user profile."""
        profile = Profile(
            user_id=user_id,
            handle=handle,
            level=level,
            xp=xp,
            avatar_layers=avatar_layers or {}
        )
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID."""
        result = await self.session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_handle(self, handle: str) -> Optional[Profile]:
        """Get profile by handle."""
        result = await self.session.execute(
            select(Profile).where(Profile.handle == handle)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        user_id: UUID,
        handle: Optional[str] = None,
        avatar_layers: Optional[dict] = None
    ) -> bool:
        """Update user profile."""
        update_data = {}
        if handle is not None:
            update_data["handle"] = handle
        if avatar_layers is not None:
            update_data["avatar_layers"] = avatar_layers

        if not update_data:
            return False

        result = await self.session.execute(
            update(Profile)
            .where(Profile.user_id == user_id)
            .values(**update_data)
        )
        return result.rowcount > 0

    async def update_user_xp(self, user_id: UUID, xp_gained: int) -> Optional[Profile]:
        """Add XP to user and update level if necessary."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        new_xp = profile.xp + xp_gained
        new_level = self._calculate_level(new_xp)

        await self.session.execute(
            update(Profile)
            .where(Profile.user_id == user_id)
            .values(xp=new_xp, level=new_level)
        )

        # Refresh the profile to get updated values
        await self.session.refresh(profile)
        return profile

    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        # Simple level calculation: level = floor(sqrt(xp / 100)) + 1
        # This gives levels at: 0, 100, 400, 900, 1600, 2500, etc.
        import math
        return max(1, int(math.sqrt(xp / 100)) + 1)

    async def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[UserStatus] = None
    ) -> List[User]:
        """List users with optional filtering."""
        query = select(User).options(selectinload(User.profile))
        
        if status:
            query = query.where(User.status == status)
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_users(self, status: Optional[UserStatus] = None) -> int:
        """Count users with optional status filter."""
        from sqlalchemy import func
        
        query = select(func.count(User.id))
        if status:
            query = query.where(User.status == status)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
