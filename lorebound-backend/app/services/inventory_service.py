"""Inventory service for managing user items and rewards."""

import logging
import random
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.inventory_repo import InventoryRepository
from ..domain.models import Item, Inventory
from ..domain.enums import ItemRarity
from .exceptions import InventoryError, ItemNotFoundError

logger = logging.getLogger(__name__)


# Rarity drop rates (percentages)
RARITY_DROP_RATES = {
    "normal_run": {
        ItemRarity.COMMON: 0.50,      # 50%
        ItemRarity.UNCOMMON: 0.30,    # 30%
        ItemRarity.RARE: 0.15,        # 15%
        ItemRarity.EPIC: 0.04,        # 4%
        ItemRarity.LEGENDARY: 0.01,    # 1%
    },
    "daily_challenge": {
        ItemRarity.COMMON: 0.10,      # 10%
        ItemRarity.UNCOMMON: 0.25,    # 25%
        ItemRarity.RARE: 0.40,        # 40%
        ItemRarity.EPIC: 0.20,        # 20%
        ItemRarity.LEGENDARY: 0.05,    # 5%
    },
}


class InventoryService:
    """Service for managing user inventory and item rewards."""

    def __init__(self):
        """Initialize inventory service."""
        pass

    async def get_user_inventory(
        self,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get user's complete inventory.
        
        Args:
            user_id: User unique identifier
            session: Database session
            
        Returns:
            Dictionary with inventory items and equipped items
        """
        inventory_repo = InventoryRepository(session)
        
        try:
            # Get all inventory items
            inventory_items = await inventory_repo.get_user_inventory(user_id)
            
            # Get equipped items by slot
            equipped_items = await inventory_repo.get_user_equipped_items(user_id)
            
            # Calculate total stats
            equipped_stats = await inventory_repo.calculate_equipped_stats(user_id)
            
            return {
                "items": [
                    {
                        "item": {
                            "id": str(inv.item.id),
                            "slug": inv.item.slug,
                            "name": inv.item.name,
                            "slot": inv.item.slot.value if hasattr(inv.item.slot, 'value') else inv.item.slot,
                            "rarity": inv.item.rarity.value if hasattr(inv.item.rarity, 'value') else inv.item.rarity,
                            "stats": inv.item.stats
                        },
                        "equipped": inv.equipped,
                        "acquired_at": inv.acquired_at.isoformat()
                    }
                    for inv in inventory_items
                ],
                "equipped_items": {
                    (slot.value if hasattr(slot, 'value') else slot): {
                        "id": str(item.id),
                        "slug": item.slug,
                        "name": item.name,
                        "slot": item.slot.value if hasattr(item.slot, 'value') else item.slot,
                        "rarity": item.rarity.value if hasattr(item.rarity, 'value') else item.rarity,
                        "stats": item.stats
                    }
                    for slot, item in equipped_items.items()
                },
                "total_stats": equipped_stats,
                "total_items": len(inventory_items)
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory for user {user_id}: {e}")
            raise InventoryError(f"Failed to get inventory: {str(e)}")

    async def equip_item(
        self,
        user_id: UUID,
        item_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Equip an item for a user.
        
        Args:
            user_id: User unique identifier
            item_id: Item unique identifier
            session: Database session
            
        Returns:
            Updated inventory data
        """
        inventory_repo = InventoryRepository(session)
        
        try:
            # Get the item to determine slot
            item = await inventory_repo.get_item_by_id(item_id)
            if not item:
                raise ItemNotFoundError(f"Item {item_id} not found")
            
            # Equip the item
            equipped_item = await inventory_repo.equip_item(user_id, item_id, item.slot)
            if not equipped_item:
                raise InventoryError(f"Failed to equip item - user may not own it")
            
            logger.info(f"User {user_id} equipped {equipped_item.name}")
            
            # Return updated inventory
            return await self.get_user_inventory(user_id, session)
            
        except (ItemNotFoundError, InventoryError):
            raise
        except Exception as e:
            logger.error(f"Error equipping item for user {user_id}: {e}")
            raise InventoryError(f"Failed to equip item: {str(e)}")

    async def distribute_run_rewards(
        self,
        user_id: UUID,
        is_daily_challenge: bool,
        is_victory: bool,
        score: int,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Distribute item rewards for completing a run.
        
        Args:
            user_id: User unique identifier
            is_daily_challenge: Whether this was a daily challenge
            is_victory: Whether the player won
            score: Player's final score
            session: Database session
            
        Returns:
            List of rewarded items
        """
        inventory_repo = InventoryRepository(session)
        
        try:
            # Determine number of reward items based on performance
            num_items = self._calculate_num_rewards(is_victory, is_daily_challenge, score)
            
            # Determine rarity distribution
            rarity_type = "daily_challenge" if is_daily_challenge else "normal_run"
            drop_rates = RARITY_DROP_RATES[rarity_type]
            
            # Get all items grouped by rarity
            all_items = await inventory_repo.list_all_items()
            items_by_rarity = {}
            for item in all_items:
                if item.rarity not in items_by_rarity:
                    items_by_rarity[item.rarity] = []
                items_by_rarity[item.rarity].append(item)
            
            # Get user's current inventory to avoid duplicates
            user_inventory = await inventory_repo.get_user_inventory(user_id)
            owned_item_ids = {inv.item_id for inv in user_inventory}
            
            # Select reward items
            rewarded_items = []
            for _ in range(num_items):
                # Roll for rarity
                rarity = self._roll_rarity(drop_rates)
                
                # Get available items of this rarity that user doesn't own
                available_items = [
                    item for item in items_by_rarity.get(rarity, [])
                    if item.id not in owned_item_ids
                ]
                
                if not available_items:
                    # If no items of this rarity available, try other rarities
                    logger.warning(f"No available items of rarity {rarity} for user {user_id}, trying other rarities...")
                    
                    # Try all rarities in order: Uncommon, Rare, Epic, Legendary, Common
                    fallback_order = [ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY, ItemRarity.COMMON]
                    
                    for fallback_rarity in fallback_order:
                        if fallback_rarity == rarity:
                            continue  # Skip the one we already tried
                        
                        available_items = [
                            item for item in items_by_rarity.get(fallback_rarity, [])
                            if item.id not in owned_item_ids
                        ]
                        
                        if available_items:
                            rarity = fallback_rarity
                            logger.info(f"Found {len(available_items)} available {fallback_rarity} items as fallback")
                            break
                    
                    if not available_items:
                        logger.warning(f"No available items of any rarity for user {user_id}, skipping reward")
                        continue
                
                # Randomly select an item
                selected_item = random.choice(available_items)
                
                # Add to user's inventory
                await inventory_repo.add_item_to_inventory(
                    user_id=user_id,
                    item_id=selected_item.id,
                    equipped=False
                )
                
                owned_item_ids.add(selected_item.id)
                rewarded_items.append({
                    "id": str(selected_item.id),
                    "slug": selected_item.slug,
                    "name": selected_item.name,
                    "slot": selected_item.slot.value if hasattr(selected_item.slot, 'value') else str(selected_item.slot),
                    "rarity": selected_item.rarity.value if hasattr(selected_item.rarity, 'value') else str(selected_item.rarity),
                    "stats": selected_item.stats
                })
                
                rarity_str = selected_item.rarity.value if hasattr(selected_item.rarity, 'value') else str(selected_item.rarity)
                logger.info(f"Rewarded {selected_item.name} ({rarity_str}) to user {user_id}")
            
            return rewarded_items
            
        except Exception as e:
            logger.error(f"Error distributing rewards to user {user_id}: {e}")
            raise InventoryError(f"Failed to distribute rewards: {str(e)}")

    def _calculate_num_rewards(self, is_victory: bool, is_daily_challenge: bool, score: int) -> int:
        """Calculate number of reward items based on performance."""
        if not is_victory:
            return 0  # No rewards for losing
        
        base_items = 1
        
        if is_daily_challenge:
            base_items = 2  # Daily challenges give more rewards
        
        # Bonus item for high scores
        if score > 5000:
            base_items += 1
        if score > 10000:
            base_items += 1
        
        return min(base_items, 3)  # Cap at 3 items per run

    def _roll_rarity(self, drop_rates: Dict[ItemRarity, float]) -> ItemRarity:
        """Roll for item rarity based on drop rates."""
        roll = random.random()
        cumulative = 0.0
        
        for rarity, rate in drop_rates.items():
            cumulative += rate
            if roll < cumulative:
                return rarity
        
        # Fallback to common if something went wrong
        return ItemRarity.COMMON

