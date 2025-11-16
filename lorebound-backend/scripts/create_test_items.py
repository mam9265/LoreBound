#!/usr/bin/env python3
"""Script to create test items with effects for testing."""

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.base import get_session
from app.domain.models import Item
from app.domain.enums import ItemSlot, ItemRarity

async def create_test_items():
    """Create test items with various effects."""
    
    test_items = [
        {
            "slug": "legendary_sword_power",
            "name": "Legendary Sword of Power",
            "slot": ItemSlot.WEAPON,
            "rarity": ItemRarity.LEGENDARY,
            "stats": {
                "score_multiplier": 1.35,
                "time_extension": 5,
                "streak_bonus": 15
            }
        },
        {
            "slug": "epic_helmet_wisdom",
            "name": "Epic Helmet of Wisdom",
            "slot": ItemSlot.HELMET,
            "rarity": ItemRarity.EPIC,
            "stats": {
                "score_multiplier": 1.15,
                "xp_bonus": 0.2
            }
        },
        {
            "slug": "epic_armor_fortitude",
            "name": "Epic Armor of Fortitude",
            "slot": ItemSlot.ARMOR,
            "rarity": ItemRarity.EPIC,
            "stats": {
                "score_multiplier": 1.1,
                "time_extension": 3
            }
        },
        {
            "slug": "rare_boots_speed",
            "name": "Rare Boots of Speed",
            "slot": ItemSlot.BOOTS,
            "rarity": ItemRarity.RARE,
            "stats": {
                "time_extension": 3,
                "xp_bonus": 0.1
            }
        },
        {
            "slug": "rare_shield_protection",
            "name": "Rare Shield of Protection",
            "slot": ItemSlot.SHIELD,
            "rarity": ItemRarity.RARE,
            "stats": {
                "score_multiplier": 1.05,
                "perfect_bonus": 10
            }
        },
        {
            "slug": "uncommon_ring_knowledge",
            "name": "Uncommon Ring of Knowledge",
            "slot": ItemSlot.RING,
            "rarity": ItemRarity.UNCOMMON,
            "stats": {
                "xp_bonus": 0.05,
                "time_extension": 2
            }
        },
        {
            "slug": "uncommon_amulet_focus",
            "name": "Uncommon Amulet of Focus",
            "slot": ItemSlot.AMULET,
            "rarity": ItemRarity.UNCOMMON,
            "stats": {
                "streak_bonus": 5
            }
        },
        {
            "slug": "common_starter_sword",
            "name": "Common Starter Sword",
            "slot": ItemSlot.WEAPON,
            "rarity": ItemRarity.COMMON,
            "stats": {
                "score_multiplier": 1.05
            }
        },
    ]
    
    print("=" * 60)
    print("Creating Test Items with Effects")
    print("=" * 60)
    
    async for session in get_session():
        try:
            from sqlalchemy import select
            
            created_count = 0
            updated_count = 0
            
            for item_data in test_items:
                # Check if item already exists
                result = await session.execute(
                    select(Item).where(Item.slug == item_data["slug"])
                )
                existing_item = result.scalar_one_or_none()
                
                if existing_item:
                    # Update stats
                    existing_item.stats = item_data["stats"]
                    updated_count += 1
                    print(f"✓ Updated: {item_data['name']} ({item_data['rarity'].value})")
                else:
                    # Create new item
                    item = Item(
                        id=uuid.uuid4(),
                        slug=item_data["slug"],
                        name=item_data["name"],
                        slot=item_data["slot"],
                        rarity=item_data["rarity"],
                        stats=item_data["stats"]
                    )
                    session.add(item)
                    created_count += 1
                    print(f"✓ Created: {item_data['name']} ({item_data['rarity'].value})")
                    print(f"  Stats: {item_data['stats']}")
            
            await session.commit()
            
            print("\n" + "=" * 60)
            print(f"✅ Created {created_count} items, Updated {updated_count} items")
            print("=" * 60)
            
            # Show all items with stats
            result = await session.execute(select(Item))
            all_items = result.scalars().all()
            
            print(f"\nTotal items in database: {len(all_items)}")
            print("\nAll items with effects:")
            for item in all_items:
                if item.stats:
                    print(f"  • {item.name} ({item.rarity}): {item.stats}")
            
            print("\n" + "=" * 60)
            print("To add these items to your inventory, use:")
            print("  python scripts/add_items_to_user.py YOUR_USER_ID")
            print("\nOr manually equip them in Character Customization screen!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(create_test_items())

