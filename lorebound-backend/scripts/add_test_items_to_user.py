#!/usr/bin/env python3
"""Add test items to a user's inventory."""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.base import get_session
from app.domain.models import Item, Inventory, User
from sqlalchemy import select

async def add_items_to_user(email: str = None):
    """Add test items to user's inventory."""
    
    print("=" * 60)
    print("Adding Test Items to User Inventory")
    print("=" * 60)
    
    async for session in get_session():
        try:
            # Get user
            if email:
                result = await session.execute(select(User).where(User.email == email))
            else:
                result = await session.execute(select(User).limit(1))
            
            user = result.scalar_one_or_none()
            if not user:
                print("❌ No user found")
                if email:
                    print(f"   Email '{email}' not in database")
                else:
                    print("   No users in database. Create an account first!")
                return
            
            print(f"\n✓ Found user: {user.email or 'No email'} (ID: {user.id})")
            
            # Get test items (items with gameplay stats)
            test_item_slugs = [
                'legendary_sword_power',
                'epic_helmet_wisdom',
                'epic_armor_fortitude',
                'rare_boots_speed',
                'rare_shield_protection',
                'uncommon_ring_knowledge',
                'uncommon_amulet_focus',
            ]
            
            result = await session.execute(
                select(Item).where(Item.slug.in_(test_item_slugs))
            )
            items = list(result.scalars().all())
            
            if not items:
                print("\n❌ No test items found!")
                print("   Run: python scripts/create_test_items.py")
                return
            
            print(f"\n✓ Found {len(items)} test items to add")
            
            added_count = 0
            already_had = 0
            
            for item in items:
                # Check if user already has this item
                inv_result = await session.execute(
                    select(Inventory).where(
                        Inventory.user_id == user.id,
                        Inventory.item_id == item.id
                    )
                )
                existing_inv = inv_result.scalar_one_or_none()
                
                if existing_inv:
                    already_had += 1
                    print(f"  ⚠ Already has: {item.name}")
                else:
                    # Add to inventory (not equipped by default)
                    inv = Inventory(
                        user_id=user.id,
                        item_id=item.id,
                        equipped=False
                    )
                    session.add(inv)
                    added_count += 1
                    print(f"  ✓ Added: {item.name} ({item.rarity})")
                    print(f"    Stats: {item.stats}")
            
            await session.commit()
            
            print("\n" + "=" * 60)
            print(f"✅ Added {added_count} items, {already_had} already owned")
            print("=" * 60)
            
            if added_count > 0:
                print("\nNext steps:")
                print("1. Open the game")
                print("2. Go to Character Customization")
                print("3. Equip the new items")
                print("4. Start a dungeon run")
                print("5. See the green bonus banner and higher scores!")
            else:
                print("\nUser already has all test items!")
                print("Equip them in Character Customization to test effects.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    # Get email from command line args
    email = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(add_items_to_user(email))

