#!/usr/bin/env python3
"""
Seed items for character customization with different rarities.
Items are equipment that players can collect from dungeon runs.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.domain.models import Item
from app.domain.enums import ItemSlot, ItemRarity
from app.core.config import get_settings


# Item definitions with stats based on rarity
ITEMS = [
    # HELMETS
    {
        "slug": "leather_cap",
        "name": "Leather Cap",
        "slot": ItemSlot.HELMET,
        "rarity": ItemRarity.COMMON,
        "stats": {"defense": 5, "intelligence": 2}
    },
    {
        "slug": "iron_helm",
        "name": "Iron Helm",
        "slot": ItemSlot.HELMET,
        "rarity": ItemRarity.RARE,
        "stats": {"defense": 15, "intelligence": 5, "speed_bonus": 0.05}
    },
    {
        "slug": "mage_hood",
        "name": "Mage Hood",
        "slot": ItemSlot.HELMET,
        "rarity": ItemRarity.EPIC,
        "stats": {"defense": 10, "intelligence": 25, "wisdom": 15, "speed_bonus": 0.10}
    },
    {
        "slug": "crown_of_thorns",
        "name": "Crown of Thorns",
        "slot": ItemSlot.HELMET,
        "rarity": ItemRarity.LEGENDARY,
        "stats": {"defense": 30, "intelligence": 40, "wisdom": 30, "speed_bonus": 0.15, "score_multiplier": 1.1}
    },
    
    # ARMOR
    {
        "slug": "travelers_tunic",
        "name": "Traveler's Tunic",
        "slot": ItemSlot.ARMOR,
        "rarity": ItemRarity.COMMON,
        "stats": {"defense": 10, "speed_bonus": 0.02}
    },
    {
        "slug": "chainmail",
        "name": "Chainmail",
        "slot": ItemSlot.ARMOR,
        "rarity": ItemRarity.RARE,
        "stats": {"defense": 25, "intelligence": 5, "speed_bonus": 0.07}
    },
    {
        "slug": "mage_robe",
        "name": "Mage Robe",
        "slot": ItemSlot.ARMOR,
        "rarity": ItemRarity.EPIC,
        "stats": {"defense": 20, "intelligence": 30, "wisdom": 20, "speed_bonus": 0.12}
    },
    {
        "slug": "dark_plate",
        "name": "Dark Plate",
        "slot": ItemSlot.ARMOR,
        "rarity": ItemRarity.LEGENDARY,
        "stats": {"defense": 50, "intelligence": 35, "wisdom": 25, "speed_bonus": 0.18, "score_multiplier": 1.15}
    },
    
    # WEAPONS
    {
        "slug": "iron_sword",
        "name": "Iron Sword",
        "slot": ItemSlot.WEAPON,
        "rarity": ItemRarity.COMMON,
        "stats": {"attack": 8, "accuracy": 0.03}
    },
    {
        "slug": "battle_axe",
        "name": "Battle Axe",
        "slot": ItemSlot.WEAPON,
        "rarity": ItemRarity.RARE,
        "stats": {"attack": 20, "intelligence": 8, "accuracy": 0.08}
    },
    {
        "slug": "magic_staff",
        "name": "Magic Staff",
        "slot": ItemSlot.WEAPON,
        "rarity": ItemRarity.EPIC,
        "stats": {"attack": 15, "intelligence": 35, "wisdom": 25, "accuracy": 0.15}
    },
    {
        "slug": "legendary_sword_of_wisdom",
        "name": "Legendary Sword of Wisdom",
        "slot": ItemSlot.WEAPON,
        "rarity": ItemRarity.LEGENDARY,
        "stats": {"attack": 40, "intelligence": 50, "wisdom": 40, "accuracy": 0.20, "score_multiplier": 1.2}
    },
    
    # SHIELDS
    {
        "slug": "wooden_shield",
        "name": "Wooden Shield",
        "slot": ItemSlot.SHIELD,
        "rarity": ItemRarity.COMMON,
        "stats": {"defense": 8, "lives_bonus": 0}
    },
    {
        "slug": "iron_shield",
        "name": "Iron Shield",
        "slot": ItemSlot.SHIELD,
        "rarity": ItemRarity.RARE,
        "stats": {"defense": 20, "intelligence": 5, "lives_bonus": 1}
    },
    {
        "slug": "magic_barrier",
        "name": "Magic Barrier",
        "slot": ItemSlot.SHIELD,
        "rarity": ItemRarity.EPIC,
        "stats": {"defense": 25, "intelligence": 20, "wisdom": 15, "lives_bonus": 1}
    },
    {
        "slug": "aegis_of_knowledge",
        "name": "Aegis of Knowledge",
        "slot": ItemSlot.SHIELD,
        "rarity": ItemRarity.LEGENDARY,
        "stats": {"defense": 45, "intelligence": 45, "wisdom": 35, "lives_bonus": 2, "score_multiplier": 1.1}
    },
    
    # Additional variety items
    {
        "slug": "scholars_cap",
        "name": "Scholar's Cap",
        "slot": ItemSlot.HELMET,
        "rarity": ItemRarity.RARE,
        "stats": {"defense": 12, "intelligence": 18, "wisdom": 10, "speed_bonus": 0.06}
    },
    {
        "slug": "rangers_vest",
        "name": "Ranger's Vest",
        "slot": ItemSlot.ARMOR,
        "rarity": ItemRarity.RARE,
        "stats": {"defense": 22, "intelligence": 12, "speed_bonus": 0.09, "accuracy": 0.05}
    },
    {
        "slug": "crystal_dagger",
        "name": "Crystal Dagger",
        "slot": ItemSlot.WEAPON,
        "rarity": ItemRarity.EPIC,
        "stats": {"attack": 25, "intelligence": 30, "speed_bonus": 0.10, "accuracy": 0.12}
    },
    {
        "slug": "tome_shield",
        "name": "Tome Shield",
        "slot": ItemSlot.SHIELD,
        "rarity": ItemRarity.EPIC,
        "stats": {"defense": 20, "intelligence": 30, "wisdom": 25, "lives_bonus": 1, "speed_bonus": 0.08}
    },
]

# Base items that every new user gets
BASE_ITEM_SLUGS = [
    "leather_cap",
    "travelers_tunic", 
    "iron_sword",
    "wooden_shield"
]


async def seed_items():
    """Seed items into the database."""
    settings = get_settings()
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print(f"\n{'='*60}")
        print("Seeding Items")
        print(f"{'='*60}\n")
        
        created_count = 0
        updated_count = 0
        
        for item_data in ITEMS:
            # Check if item already exists
            result = await session.execute(
                select(Item).where(Item.slug == item_data["slug"])
            )
            existing_item = result.scalar_one_or_none()
            
            if existing_item:
                # Update existing item
                existing_item.name = item_data["name"]
                existing_item.slot = item_data["slot"]
                existing_item.rarity = item_data["rarity"]
                existing_item.stats = item_data["stats"]
                updated_count += 1
                print(f"  ↻ Updated: {item_data['name']} ({item_data['rarity'].value})")
            else:
                # Create new item
                new_item = Item(
                    slug=item_data["slug"],
                    name=item_data["name"],
                    slot=item_data["slot"],
                    rarity=item_data["rarity"],
                    stats=item_data["stats"]
                )
                session.add(new_item)
                created_count += 1
                print(f"  ✓ Created: {item_data['name']} ({item_data['rarity'].value})")
        
        await session.commit()
        
        print(f"\n{'='*60}")
        print(f"✓ Created {created_count} new items")
        print(f"↻ Updated {updated_count} existing items")
        print(f"Total items: {len(ITEMS)}")
        print(f"{'='*60}\n")
        
        # Show stats by rarity
        rarity_counts = {}
        for item in ITEMS:
            rarity = item["rarity"].value
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        print("Items by Rarity:")
        for rarity, count in sorted(rarity_counts.items()):
            print(f"  {rarity.capitalize()}: {count}")
        
        print(f"\nBase items for new users:")
        for slug in BASE_ITEM_SLUGS:
            item = next(i for i in ITEMS if i["slug"] == slug)
            print(f"  • {item['name']}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_items())

