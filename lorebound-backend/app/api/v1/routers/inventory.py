"""Inventory and item management endpoints."""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_active_user
from ....repositories.base import get_session
from ....services.inventory_service import InventoryService
from ....services.exceptions import InventoryError, ItemNotFoundError
from ....schemas.inventory import EquipItemRequest
from ....domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/")
async def get_inventory(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user's complete inventory.
    
    Returns all items the user owns, equipped items by slot, and total stats.
    """
    try:
        logger.info(f"Fetching inventory for user: {current_user.id}")
        inventory_service = InventoryService()
        inventory = await inventory_service.get_user_inventory(current_user.id, session)
        return inventory
        
    except Exception as e:
        logger.error(f"Error getting inventory for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get inventory"
        )


@router.post("/equip")
async def equip_item(
    equip_request: EquipItemRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Equip an item.
    
    Unequips any item currently in that slot and equips the specified item.
    """
    try:
        logger.info(f"User {current_user.id} equipping item {equip_request.item_id} in slot {equip_request.slot}")
        inventory_service = InventoryService()
        
        updated_inventory = await inventory_service.equip_item(
            user_id=current_user.id,
            item_id=equip_request.item_id,
            session=session
        )
        
        await session.commit()
        
        logger.info(f"User {current_user.id} successfully equipped item {equip_request.item_id}")
        return updated_inventory
        
    except ItemNotFoundError as e:
        logger.warning(f"Item not found for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InventoryError as e:
        logger.error(f"Inventory error for user {current_user.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error equipping item for user {current_user.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to equip item"
        )
