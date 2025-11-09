"""Inventory repository for item and equipment management."""

from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete
from sqlalchemy.orm import selectinload

from ..domain.models import Item, Inventory
from ..domain.enums import ItemSlot, ItemRarity


class InventoryRepository:
    """Repository for inventory and item-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Item operations
    async def get_item_by_id(self, item_id: UUID) -> Optional[Item]:
        """Get item by ID."""
        result = await self.session.execute(
            select(Item).where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_item_by_slug(self, slug: str) -> Optional[Item]:
        """Get item by slug."""
        result = await self.session.execute(
            select(Item).where(Item.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_items_by_slot(self, slot: ItemSlot) -> List[Item]:
        """Get all items for a specific slot."""
        result = await self.session.execute(
            select(Item)
            .where(Item.slot == slot)
            .order_by(Item.rarity, Item.name)
        )
        return list(result.scalars().all())

    async def get_items_by_rarity(self, rarity: ItemRarity) -> List[Item]:
        """Get all items of a specific rarity."""
        result = await self.session.execute(
            select(Item)
            .where(Item.rarity == rarity)
            .order_by(Item.slot, Item.name)
        )
        return list(result.scalars().all())

    async def list_all_items(self) -> List[Item]:
        """Get all items."""
        result = await self.session.execute(
            select(Item).order_by(Item.slot, Item.rarity, Item.name)
        )
        return list(result.scalars().all())

    # Inventory operations
    async def get_user_inventory(self, user_id: UUID) -> List[Inventory]:
        """Get all inventory items for a user."""
        result = await self.session.execute(
            select(Inventory)
            .options(selectinload(Inventory.item))
            .where(Inventory.user_id == user_id)
            .order_by(Inventory.acquired_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_equipped_items(self, user_id: UUID) -> Dict[ItemSlot, Item]:
        """Get user's currently equipped items by slot."""
        result = await self.session.execute(
            select(Inventory)
            .options(selectinload(Inventory.item))
            .where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.equipped == True
                )
            )
        )
        
        equipped_items = {}
        for inventory_item in result.scalars().all():
            equipped_items[inventory_item.item.slot] = inventory_item.item
        
        return equipped_items

    async def get_user_inventory_item(
        self,
        user_id: UUID,
        item_id: UUID
    ) -> Optional[Inventory]:
        """Get specific inventory item for user."""
        result = await self.session.execute(
            select(Inventory)
            .options(selectinload(Inventory.item))
            .where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.item_id == item_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def add_item_to_inventory(
        self,
        user_id: UUID,
        item_id: UUID,
        equipped: bool = False
    ) -> Inventory:
        """Add an item to user's inventory."""
        inventory_item = Inventory(
            user_id=user_id,
            item_id=item_id,
            equipped=equipped,
            acquired_at=datetime.now(timezone.utc)
        )
        self.session.add(inventory_item)
        await self.session.flush()
        await self.session.refresh(inventory_item)
        return inventory_item

    async def remove_item_from_inventory(
        self,
        user_id: UUID,
        item_id: UUID
    ) -> bool:
        """Remove an item from user's inventory."""
        result = await self.session.execute(
            delete(Inventory).where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.item_id == item_id
                )
            )
        )
        return result.rowcount > 0

    async def equip_item(
        self,
        user_id: UUID,
        item_id: UUID,
        slot: ItemSlot
    ) -> Optional[Item]:
        """Equip an item and unequip any existing item in that slot."""
        # First, verify user owns the item and it's for the correct slot
        inventory_item = await self.get_user_inventory_item(user_id, item_id)
        if not inventory_item or inventory_item.item.slot != slot:
            return None

        # Get all equipped items in this slot and unequip them
        # We need to use a SELECT to find them first, then UPDATE
        currently_equipped = await self.session.execute(
            select(Inventory)
            .options(selectinload(Inventory.item))
            .where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.equipped == True
                )
            )
        )
        
        # Unequip items in the same slot
        for inv in currently_equipped.scalars().all():
            if inv.item.slot == slot:
                inv.equipped = False

        # Equip the new item
        inventory_item.equipped = True
        await self.session.flush()

        return inventory_item.item

    async def unequip_item(
        self,
        user_id: UUID,
        item_id: UUID
    ) -> bool:
        """Unequip an item."""
        result = await self.session.execute(
            update(Inventory)
            .where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.item_id == item_id,
                    Inventory.equipped == True
                )
            )
            .values(equipped=False)
        )
        return result.rowcount > 0

    async def unequip_slot(self, user_id: UUID, slot: ItemSlot) -> bool:
        """Unequip any item in a specific slot."""
        result = await self.session.execute(
            update(Inventory)
            .where(
                and_(
                    Inventory.user_id == user_id,
                    Inventory.equipped == True
                )
            )
            .join(Item)
            .where(Item.slot == slot)
            .values(equipped=False)
        )
        return result.rowcount > 0

    async def get_user_items_by_slot(
        self,
        user_id: UUID,
        slot: ItemSlot,
        equipped_only: bool = False
    ) -> List[Inventory]:
        """Get user's items for a specific slot."""
        query = (
            select(Inventory)
            .options(selectinload(Inventory.item))
            .where(Inventory.user_id == user_id)
            .join(Item)
            .where(Item.slot == slot)
        )
        
        if equipped_only:
            query = query.where(Inventory.equipped == True)
        
        query = query.order_by(Inventory.equipped.desc(), Inventory.acquired_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_user_items(
        self,
        user_id: UUID,
        slot: Optional[ItemSlot] = None,
        rarity: Optional[ItemRarity] = None,
        equipped_only: bool = False
    ) -> int:
        """Count user's items with optional filters."""
        from sqlalchemy import func
        
        query = select(func.count(Inventory.item_id)).where(Inventory.user_id == user_id)
        
        if equipped_only:
            query = query.where(Inventory.equipped == True)
        
        if slot or rarity:
            query = query.join(Item)
            if slot:
                query = query.where(Item.slot == slot)
            if rarity:
                query = query.where(Item.rarity == rarity)
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def calculate_equipped_stats(self, user_id: UUID) -> Dict[str, float]:
        """Calculate total stats from all equipped items."""
        equipped_items = await self.get_user_equipped_items(user_id)
        
        total_stats = {}
        for item in equipped_items.values():
            for stat_name, stat_value in item.stats.items():
                if isinstance(stat_value, (int, float)):
                    total_stats[stat_name] = total_stats.get(stat_name, 0) + stat_value
        
        return total_stats

    async def get_inventory_summary(self, user_id: UUID) -> Dict[str, any]:
        """Get inventory summary statistics."""
        from sqlalchemy import func
        
        # Total items
        total_items = await self.count_user_items(user_id)
        
        # Items by slot
        items_by_slot = {}
        for slot in ItemSlot:
            count = await self.count_user_items(user_id, slot=slot)
            items_by_slot[slot.value] = count
        
        # Items by rarity
        items_by_rarity = {}
        for rarity in ItemRarity:
            count = await self.count_user_items(user_id, rarity=rarity)
            items_by_rarity[rarity.value] = count
        
        # Equipped items count
        equipped_count = await self.count_user_items(user_id, equipped_only=True)
        
        # Total stats from equipped items
        equipped_stats = await self.calculate_equipped_stats(user_id)
        
        return {
            "total_items": total_items,
            "equipped_items": equipped_count,
            "items_by_slot": items_by_slot,
            "items_by_rarity": items_by_rarity,
            "equipped_stats": equipped_stats
        }
