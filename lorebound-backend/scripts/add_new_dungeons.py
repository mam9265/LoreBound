#!/usr/bin/env python3
"""Script to add new dungeon categories without affecting existing ones."""

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.base import get_session
from app.repositories.content_repo import ContentRepository
from app.domain.models import Dungeon, DungeonTier
from app.domain.enums import DungeonCategory

async def add_new_dungeons():
    """Add new dungeon types if they don't exist."""
    
    new_dungeons_data = [
        {
            "title": "Library of Knowledge",
            "category": DungeonCategory.BOOKS,
            "modifiers": {
                "description": "Explore the vast realm of literature and storytelling",
                "difficulty": "medium",
                "estimated_duration": "15-20 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Bookworm Guardian", "description": "Protector of written wisdom"}},
                {"floor": 2, "boss_meta": {"name": "Literary Master", "description": "Keeper of classic tales"}},
            ]
        },
        {
            "title": "Science Laboratory",
            "category": DungeonCategory.SCIENCE,
            "modifiers": {
                "description": "Discover the mysteries of science and nature",
                "difficulty": "hard",
                "estimated_duration": "18-22 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Lab Technician", "description": "Master of experiments"}},
                {"floor": 2, "boss_meta": {"name": "Research Professor", "description": "Expert of scientific method"}},
            ]
        },
        {
            "title": "Geography Explorer",
            "category": DungeonCategory.GEOGRAPHY,
            "modifiers": {
                "description": "Journey across the world's landscapes and cultures",
                "difficulty": "medium",
                "estimated_duration": "12-18 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "World Traveler", "description": "Explorer of distant lands"}},
                {"floor": 2, "boss_meta": {"name": "Cartographer", "description": "Master mapmaker"}},
            ]
        },
        {
            "title": "General Knowledge Arena",
            "category": DungeonCategory.GENERAL,
            "modifiers": {
                "description": "Test your knowledge across all subjects",
                "difficulty": "medium",
                "estimated_duration": "15-20 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Quiz Master", "description": "Guardian of general trivia"}},
                {"floor": 2, "boss_meta": {"name": "Knowledge Sage", "description": "Keeper of all wisdom"}},
            ]
        }
    ]
    
    async for session in get_session():
        try:
            content_repo = ContentRepository(session)
            
            # Get existing dungeons
            existing_dungeons = await content_repo.get_all_dungeons()
            # Handle both enum and string categories
            existing_categories = set()
            for d in existing_dungeons:
                if isinstance(d.category, str):
                    existing_categories.add(d.category)
                else:
                    existing_categories.add(d.category.value if hasattr(d.category, 'value') else str(d.category))
            
            print(f"Found {len(existing_dungeons)} existing dungeons")
            print(f"Existing categories: {list(existing_categories)}")
            
            added_count = 0
            
            for dungeon_data in new_dungeons_data:
                category = dungeon_data["category"]
                category_value = category.value if hasattr(category, 'value') else str(category)
                
                # Check if this category already exists
                if category_value in existing_categories:
                    print(f"⚠ Skipping {dungeon_data['title']} - category '{category_value}' already exists")
                    continue
                
                # Create new dungeon
                dungeon = Dungeon(
                    id=uuid.uuid4(),
                    title=dungeon_data["title"],
                    category=category,
                    modifiers=dungeon_data["modifiers"],
                    content_version=1
                )
                
                session.add(dungeon)
                await session.flush()
                
                # Create tiers
                for tier_data in dungeon_data["tiers"]:
                    tier = DungeonTier(
                        id=uuid.uuid4(),
                        dungeon_id=dungeon.id,
                        floor=tier_data["floor"],
                        boss_meta=tier_data["boss_meta"]
                    )
                    session.add(tier)
                
                print(f"✓ Added dungeon: {dungeon.title} ({category_value})")
                added_count += 1
            
            await session.commit()
            
            if added_count > 0:
                print(f"\n✅ Successfully added {added_count} new dungeons!")
            else:
                print("\n✅ All dungeon categories already exist!")
            
        except Exception as e:
            print(f"❌ Failed to add dungeons: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(add_new_dungeons())

