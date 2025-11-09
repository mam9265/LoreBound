#!/usr/bin/env python3
"""
Give base items to existing users who don't have any items yet.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.domain.models import User, Item, Inventory
from app.core.config import get_settings

BASE_ITEM_SLUGS = ["leather_cap", "travelers_tunic", "iron_sword", "wooden_shield"]

async def give_base_items():
    """Give base items to users without any items."""
    settings = get_settings()
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print(f"\n{'='*60}")
        print("Giving Base Items to Existing Users")
        print(f"{'='*60}\n")
        
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        # Get base items
        base_items = {}
        for slug in BASE_ITEM_SLUGS:
            item_result = await session.execute(select(Item).where(Item.slug == slug))
            item = item_result.scalar_one_or_none()
            if item:
                base_items[slug] = item
        
        print(f"Found {len(users)} users")
        print(f"Base items: {', '.join([i.name for i in base_items.values()])}\n")
        
        users_updated = 0
        items_added = 0
        
        for user in users:
            # Check if user has any items
            inv_result = await session.execute(
                select(Inventory).where(Inventory.user_id == user.id).limit(1)
            )
            has_items = inv_result.scalar_one_or_none() is not None
            
            if not has_items:
                print(f"User {user.id} has no items, giving base items...")
                for slug, item in base_items.items():
                    new_inv = Inventory(
                        user_id=user.id,
                        item_id=item.id,
                        equipped=True
                    )
                    session.add(new_inv)
                    items_added += 1
                    print(f"  ✓ Added {item.name}")
                users_updated += 1
            else:
                print(f"  User {user.id} already has items, skipping")
        
        await session.commit()
        
        print(f"\n{'='*60}")
        print(f"✓ Updated {users_updated} users")
        print(f"✓ Added {items_added} items total")
        print(f"{'='*60}\n")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(give_base_items())

