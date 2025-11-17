#!/usr/bin/env python3
"""
Give all items to a specific user for testing.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.domain.models import User, Item, Inventory, Profile
from app.core.config import get_settings

async def give_all_items_to_user(email: str):
    """Give all items to a specific user."""
    settings = get_settings()
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print(f"\n{'='*60}")
        print(f"Giving All Items to User: {email}")
        print(f"{'='*60}\n")
        
        # Find user by email
        user_result = await session.execute(
            select(User).where(User.email == email.lower())
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            print(f"✗ User not found: {email}")
            return
        
        # Get user's profile
        profile_result = await session.execute(
            select(Profile).where(Profile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()
        
        print(f"✓ Found user: {user.id}")
        if profile:
            print(f"  Handle: {profile.handle}")
        
        # Get all items
        items_result = await session.execute(select(Item))
        all_items = items_result.scalars().all()
        
        print(f"✓ Found {len(all_items)} items in database\n")
        
        # Get user's current inventory
        inventory_result = await session.execute(
            select(Inventory).where(Inventory.user_id == user.id)
        )
        existing_inventory = {inv.item_id for inv in inventory_result.scalars().all()}
        
        # Add all missing items
        added_count = 0
        for item in all_items:
            if item.id not in existing_inventory:
                new_inv = Inventory(
                    user_id=user.id,
                    item_id=item.id,
                    equipped=False  # Don't auto-equip
                )
                session.add(new_inv)
                added_count += 1
                print(f"  ✓ Added: {item.name} ({item.rarity.value if hasattr(item.rarity, 'value') else item.rarity})")
        
        await session.commit()
        
        print(f"\n{'='*60}")
        print(f"✓ Added {added_count} new items")
        print(f"✓ User already had {len(existing_inventory)} items")
        print(f"Total items: {len(all_items)}")
        print(f"{'='*60}\n")
    
    await engine.dispose()

if __name__ == "__main__":
    # User email to give items to
    user_email = "mdmattern@icloud.com"
    asyncio.run(give_all_items_to_user(user_email))

