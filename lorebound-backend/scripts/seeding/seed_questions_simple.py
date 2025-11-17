#!/usr/bin/env python3
"""Simple script to seed questions."""

import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.repositories.base import get_session
from app.domain.models import Question, Dungeon
from app.domain.enums import DungeonCategory, QuestionDifficulty
from sqlalchemy import select, func

async def seed_questions():
    """Create sample questions for testing."""
    
    async for session in get_session():
        try:
            # Check if questions already exist
            result = await session.execute(select(func.count(Question.id)))
            question_count = result.scalar() or 0
            if question_count > 0:
                print(f"Database already has {question_count} questions. Skipping seeding.")
                return
            
            # Get dungeons
            dungeons_result = await session.execute(select(Dungeon))
            dungeons = list(dungeons_result.scalars().all())
            
            if not dungeons:
                print("[ERROR] No dungeons found. Please seed dungeons first.")
                return
            
            # Map categories to dungeons
            dungeon_map = {dungeon.category: dungeon for dungeon in dungeons}
            
            print(f"Found {len(dungeons)} dungeons. Creating questions...")
            
            questions_data = [
                # History questions
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
                    "prompt": "In what year did World War II end?",
                    "choices": ["1943", "1944", "1945", "1946"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.HISTORY,
                    "tags": ["history", "world war", "20th century"]
                },
                {
                    "prompt": "Which empire was ruled by Genghis Khan?",
                    "choices": ["Ottoman", "Mongol", "Persian", "Roman"],
                    "answer_index": 1,
                    "difficulty": QuestionDifficulty.MEDIUM,
                    "category": DungeonCategory.HISTORY,
                    "tags": ["history", "mongol", "medieval"]
                },
                # Sports questions
                {
                    "prompt": "In which sport would you perform a slam dunk?",
                    "choices": ["Soccer", "Tennis", "Basketball", "Volleyball"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.SPORTS,
                    "tags": ["sports", "basketball", "basic"]
                },
                {
                    "prompt": "How many players are on a soccer team?",
                    "choices": ["9", "10", "11", "12"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.SPORTS,
                    "tags": ["sports", "soccer", "rules"]
                },
                {
                    "prompt": "Which country has won the most FIFA World Cups?",
                    "choices": ["Germany", "Argentina", "Brazil", "Italy"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.MEDIUM,
                    "category": DungeonCategory.SPORTS,
                    "tags": ["sports", "soccer", "world cup"]
                },
                # Music questions
                {
                    "prompt": "Which composer wrote 'The Four Seasons'?",
                    "choices": ["Mozart", "Bach", "Vivaldi", "Beethoven"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.MEDIUM,
                    "category": DungeonCategory.MUSIC,
                    "tags": ["music", "classical", "composer", "baroque"]
                },
                {
                    "prompt": "How many strings does a standard guitar have?",
                    "choices": ["4", "5", "6", "7"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.MUSIC,
                    "tags": ["music", "instruments", "guitar"]
                },
                {
                    "prompt": "Which band sang 'Bohemian Rhapsody'?",
                    "choices": ["The Beatles", "Queen", "Led Zeppelin", "Pink Floyd"],
                    "answer_index": 1,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.MUSIC,
                    "tags": ["music", "rock", "queen"]
                },
                # Pop Culture questions
                {
                    "prompt": "What TV show featured the characters Ross, Rachel, and Monica?",
                    "choices": ["Seinfeld", "Friends", "Cheers", "Frasier"],
                    "answer_index": 1,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.POP_CULTURE,
                    "tags": ["tv", "sitcom", "90s", "friends"]
                },
                {
                    "prompt": "Which movie won the Oscar for Best Picture in 1994?",
                    "choices": ["Pulp Fiction", "Forrest Gump", "The Shawshank Redemption", "The Lion King"],
                    "answer_index": 1,
                    "difficulty": QuestionDifficulty.HARD,
                    "category": DungeonCategory.POP_CULTURE,
                    "tags": ["movies", "oscars", "90s"]
                },
                {
                    "prompt": "Who played Iron Man in the Marvel Cinematic Universe?",
                    "choices": ["Chris Evans", "Chris Hemsworth", "Robert Downey Jr.", "Mark Ruffalo"],
                    "answer_index": 2,
                    "difficulty": QuestionDifficulty.EASY,
                    "category": DungeonCategory.POP_CULTURE,
                    "tags": ["movies", "marvel", "superheroes"]
                }
            ]
            
            created_count = 0
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
                created_count += 1
            
            await session.commit()
            print(f"[SUCCESS] Created {created_count} questions successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to seed questions: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(seed_questions())

