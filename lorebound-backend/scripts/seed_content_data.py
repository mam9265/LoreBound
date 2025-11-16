#!/usr/bin/env python3
"""Script to seed the database with sample content data."""

import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.base import get_session
from app.repositories.content_repo import ContentRepository
from app.domain.models import Dungeon, DungeonTier, Question
from app.domain.enums import DungeonCategory, QuestionDifficulty

async def seed_dungeons():
    """Create sample dungeons with tiers."""
    
    dungeons_data = [
        {
            "title": "Ancient History Depths",
            "category": DungeonCategory.HISTORY,
            "modifiers": {
                "description": "Journey through ancient civilizations",
                "difficulty": "medium",
                "estimated_duration": "15-20 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Guardian of Knowledge", "description": "Ancient keeper of historical wisdom"}},
                {"floor": 2, "boss_meta": {"name": "Pharaoh's Spirit", "description": "Ruler of the ancient sands"}},
                {"floor": 3, "boss_meta": {"name": "Roman Centurion", "description": "Elite warrior of the empire"}},
            ]
        },
        {
            "title": "Sports Arena Challenge",
            "category": DungeonCategory.SPORTS,
            "modifiers": {
                "description": "Test your sports knowledge across all disciplines",
                "difficulty": "medium",
                "estimated_duration": "10-15 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Coach Champion", "description": "Master of athletic wisdom"}},
                {"floor": 2, "boss_meta": {"name": "Olympic Hero", "description": "Legend of competitive sports"}},
            ]
        },
        {
            "title": "Musical Harmony Tower",
            "category": DungeonCategory.MUSIC,
            "modifiers": {
                "description": "Climb the tower of musical mastery",
                "difficulty": "easy",
                "estimated_duration": "12-18 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Melody Keeper", "description": "Guardian of ancient songs"}},
                {"floor": 2, "boss_meta": {"name": "Harmony Master", "description": "Composer of legendary pieces"}},
                {"floor": 3, "boss_meta": {"name": "Symphony Conductor", "description": "Orchestrator of perfect sound"}},
            ]
        },
        {
            "title": "Pop Culture Arcade",
            "category": DungeonCategory.POP_CULTURE,
            "modifiers": {
                "description": "Navigate through decades of popular culture",
                "difficulty": "hard",
                "estimated_duration": "20-25 minutes"
            },
            "tiers": [
                {"floor": 1, "boss_meta": {"name": "Trend Setter", "description": "Pioneer of cultural movements"}},
                {"floor": 2, "boss_meta": {"name": "Media Mogul", "description": "Controller of entertainment empires"}},
            ]
        },
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
            
            # Check if dungeons already exist
            existing_dungeons = await content_repo.get_all_dungeons()
            if existing_dungeons:
                print(f"Database already has {len(existing_dungeons)} dungeons. Skipping seeding.")
                return
            
            print("Seeding dungeons...")
            
            for dungeon_data in dungeons_data:
                # Create dungeon
                dungeon = Dungeon(
                    id=uuid.uuid4(),
                    title=dungeon_data["title"],
                    category=dungeon_data["category"],
                    modifiers=dungeon_data["modifiers"],
                    content_version=1
                )
                
                session.add(dungeon)
                await session.flush()  # Get the dungeon ID
                
                # Create tiers
                for tier_data in dungeon_data["tiers"]:
                    tier = DungeonTier(
                        id=uuid.uuid4(),
                        dungeon_id=dungeon.id,
                        floor=tier_data["floor"],
                        boss_meta=tier_data["boss_meta"]
                    )
                    session.add(tier)
                
                print(f"Created dungeon: {dungeon.title} with {len(dungeon_data['tiers'])} tiers")
            
            await session.commit()
            print("[SUCCESS] Dungeons seeded successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to seed dungeons: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

async def seed_questions():
    """Create sample questions for testing."""
    
    questions_data = [
        {
            "prompt": "Which ancient civilization built the pyramids of Giza?",
            "choices": ["Romans", "Egyptians", "Greeks", "Babylonians"],
            "answer_index": 1,
            "difficulty": QuestionDifficulty.EASY,
            "category": DungeonCategory.HISTORY,
            "tags": ["history", "ancient", "egypt", "pyramids"]
        },
        {
            "prompt": "Who was the first emperor of Rome?",
            "choices": ["Julius Caesar", "Augustus", "Nero", "Caligula"],
            "answer_index": 1,
            "difficulty": QuestionDifficulty.MEDIUM,
            "category": DungeonCategory.HISTORY,
            "tags": ["history", "ancient", "rome", "emperor"]
        },
        {
            "prompt": "In which sport would you perform a slam dunk?",
            "choices": ["Soccer", "Tennis", "Basketball", "Volleyball"],
            "answer_index": 2,
            "difficulty": QuestionDifficulty.EASY,
            "category": DungeonCategory.SPORTS,
            "tags": ["sports", "basketball", "basic"]
        },
        {
            "prompt": "Which composer wrote 'The Four Seasons'?",
            "choices": ["Mozart", "Bach", "Vivaldi", "Beethoven"],
            "answer_index": 2,
            "difficulty": QuestionDifficulty.MEDIUM,
            "category": DungeonCategory.MUSIC,
            "tags": ["music", "classical", "composer", "baroque"]
        },
        {
            "prompt": "What TV show featured the characters Ross, Rachel, and Monica?",
            "choices": ["Seinfeld", "Friends", "Cheers", "Frasier"],
            "answer_index": 1,
            "difficulty": QuestionDifficulty.EASY,
            "category": DungeonCategory.POP_CULTURE,
            "tags": ["tv", "sitcom", "90s", "friends"]
        }
    ]
    
    async for session in get_session():
        try:
            content_repo = ContentRepository(session)
            
            # Get dungeons to link questions to
            dungeons = await content_repo.get_all_dungeons()
            if not dungeons:
                print("[ERROR] No dungeons found. Please seed dungeons first.")
                return
            
            # Check if questions already exist by counting total questions
            from sqlalchemy import select, func
            from app.domain.models import Question as QuestionModel
            result = await session.execute(select(func.count(QuestionModel.id)))
            question_count = result.scalar() or 0
            if question_count > 0:
                print(f"Database already has {question_count} questions. Skipping seeding.")
                return
            
            print("Seeding questions...")
            
            # Map categories to dungeons
            dungeon_map = {dungeon.category: dungeon for dungeon in dungeons}
            
            for question_data in questions_data:
                category = question_data["category"]
                if category not in dungeon_map:
                    print(f"[WARNING] No dungeon found for category: {category}")
                    continue
                
                dungeon = dungeon_map[category]
                
                question = Question(
                    id=uuid.uuid4(),
                    dungeon_id=dungeon.id,
                    prompt=question_data["prompt"],
                    choices=question_data["choices"],
                    answer_index=question_data["answer_index"],
                    difficulty=question_data["difficulty"],
                    tags=question_data["tags"]
                )
                
                session.add(question)
                print(f"Created question: {question.prompt[:50]}...")
            
            await session.commit()
            print("[SUCCESS] Questions seeded successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to seed questions: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

async def main():
    """Seed all content data."""
    print("=== SEEDING CONTENT DATA ===")
    
    try:
        await seed_dungeons()
        await seed_questions()
        print("\n[SUCCESS] All content data seeded successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Content seeding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
