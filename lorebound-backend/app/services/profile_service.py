"""Profile service for user profile and character customization operations."""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.user_repo import UserRepository
from ..repositories.inventory_repo import InventoryRepository
from ..domain.models import Profile
from .exceptions import ProfileError, ProfileNotFoundError, HandleAlreadyExistsError

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles and character customization."""

    def __init__(self):
        """Initialize profile service."""
        pass

    async def get_user_profile(
        self,
        user_id: UUID,
        session: AsyncSession
    ) -> Profile:
        """
        Get user profile by user ID.
        
        Args:
            user_id: User unique identifier
            session: Database session
            
        Returns:
            User profile
            
        Raises:
            ProfileNotFoundError: If profile not found
        """
        user_repo = UserRepository(session)
        
        try:
            profile = await user_repo.get_profile_by_user_id(user_id)
            
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for user: {user_id}")
            
            logger.info(f"Retrieved profile for user: {user_id}")
            return profile
            
        except ProfileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting profile for user {user_id}: {e}")
            raise ProfileError(f"Failed to get profile: {str(e)}")

    async def update_user_profile(
        self,
        user_id: UUID,
        handle: Optional[str] = None,
        avatar_layers: Optional[Dict[str, Any]] = None,
        session: AsyncSession = None
    ) -> Profile:
        """
        Update user profile.
        
        Args:
            user_id: User unique identifier
            handle: New display name (optional)
            avatar_layers: Avatar customization data (optional)
            session: Database session
            
        Returns:
            Updated profile
            
        Raises:
            ProfileNotFoundError: If profile not found
            HandleAlreadyExistsError: If handle is already taken
            ProfileError: For other errors
        """
        user_repo = UserRepository(session)
        
        try:
            # Check if profile exists
            profile = await user_repo.get_profile_by_user_id(user_id)
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for user: {user_id}")
            
            # If handle is being updated, check if it's available
            if handle and handle != profile.handle:
                existing_profile = await user_repo.get_profile_by_handle(handle)
                if existing_profile:
                    raise HandleAlreadyExistsError(f"Handle '{handle}' is already taken")
            
            # Update profile
            success = await user_repo.update_profile(
                user_id=user_id,
                handle=handle,
                avatar_layers=avatar_layers
            )
            
            if not success:
                raise ProfileError("Failed to update profile")
            
            # Retrieve updated profile
            updated_profile = await user_repo.get_profile_by_user_id(user_id)
            
            logger.info(f"Updated profile for user: {user_id}")
            return updated_profile
            
        except (ProfileNotFoundError, HandleAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            raise ProfileError(f"Failed to update profile: {str(e)}")

    async def update_character_customization(
        self,
        user_id: UUID,
        customization_data: Dict[str, Any],
        session: AsyncSession
    ) -> Profile:
        """
        Update character customization (avatar_layers).
        
        This is a convenience method specifically for character customization
        from the mobile app.
        
        Args:
            user_id: User unique identifier
            customization_data: Character customization data (equipment, colors, etc.)
            session: Database session
            
        Returns:
            Updated profile
            
        Raises:
            ProfileNotFoundError: If profile not found
            ProfileError: For other errors
        """
        return await self.update_user_profile(
            user_id=user_id,
            avatar_layers=customization_data,
            session=session
        )

    async def get_profile_with_inventory(
        self,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get user profile with inventory summary.
        
        Args:
            user_id: User unique identifier
            session: Database session
            
        Returns:
            Dictionary with profile and inventory data
            
        Raises:
            ProfileNotFoundError: If profile not found
        """
        user_repo = UserRepository(session)
        inventory_repo = InventoryRepository(session)
        
        try:
            profile = await user_repo.get_profile_by_user_id(user_id)
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for user: {user_id}")
            
            # Get equipped items
            equipped_items = await inventory_repo.get_user_equipped_items(user_id)
            
            # Get equipped stats
            equipped_stats = await inventory_repo.calculate_equipped_stats(user_id)
            
            return {
                "profile": profile,
                "equipped_items": equipped_items,
                "equipped_stats": equipped_stats
            }
            
        except ProfileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting profile with inventory for user {user_id}: {e}")
            raise ProfileError(f"Failed to get profile with inventory: {str(e)}")

