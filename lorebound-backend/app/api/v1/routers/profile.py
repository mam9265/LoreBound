"""User profile endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_active_user
from ....services.dependencies import get_profile_service_with_session
from ....services.profile_service import ProfileService
from ....services.exceptions import (
    ProfileNotFoundError,
    HandleAlreadyExistsError,
    ProfileError
)
from ....schemas.user import ProfileResponse, ProfileUpdateRequest
from ....domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    service_session: tuple[ProfileService, AsyncSession] = Depends(get_profile_service_with_session)
) -> ProfileResponse:
    """
    Get current user's profile.
    
    Returns user profile including handle, level, XP, and character customization (avatar_layers).
    """
    profile_service, session = service_session
    
    try:
        logger.info(f"Fetching profile for user: {current_user.id}")
        profile = await profile_service.get_user_profile(current_user.id, session)
        return ProfileResponse.model_validate(profile)
        
    except ProfileNotFoundError as e:
        logger.error(f"Profile not found for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    except Exception as e:
        logger.error(f"Error getting profile for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile"
        )


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    service_session: tuple[ProfileService, AsyncSession] = Depends(get_profile_service_with_session)
) -> ProfileResponse:
    """
    Update current user's profile.
    
    Allows updating:
    - handle: Display name (must be unique)
    - avatar_layers: Character customization data (equipment, colors, etc.)
    """
    profile_service, session = service_session
    
    try:
        logger.info(f"Updating profile for user: {current_user.id}")
        
        updated_profile = await profile_service.update_user_profile(
            user_id=current_user.id,
            handle=profile_data.handle,
            avatar_layers=profile_data.avatar_layers,
            session=session
        )
        
        # Commit the transaction
        await session.commit()
        
        logger.info(f"Profile updated successfully for user: {current_user.id}")
        return ProfileResponse.model_validate(updated_profile)
        
    except ProfileNotFoundError as e:
        logger.error(f"Profile not found for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    except HandleAlreadyExistsError as e:
        logger.warning(f"Handle already exists for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ProfileError as e:
        logger.error(f"Profile error for user {current_user.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating profile for user {current_user.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
