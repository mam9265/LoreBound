#!/usr/bin/env python3
"""Script to clear old incorrectly categorized questions and repopulate with correct mapping."""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.repositories.base import get_session
from app.domain.models import Question
from app.repositories.content_repo import ContentRepository
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient
from app.core.config import settings
from sqlalchemy import delete

async def clear_and_repopulate():
    """Clear old questions and repopulate with correct category mapping."""
    print("=" * 60)
    print("Clearing Old Questions and Repopulating")
    print("=" * 60)
    
    async for session in get_session():
        try:
            # Count existing questions
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(Question.id)))
            old_count = result.scalar() or 0
            print(f"\nFound {old_count} existing questions")
            
            if old_count > 0:
                print("Deleting old incorrectly categorized questions...")
                await session.execute(delete(Question))
                await session.commit()
                print("✓ Deleted all old questions")
            
            print("\nRepopulating with correct category mapping...")
            print("This will take ~10-15 minutes due to OpenTDB rate limiting...")
            print()
            
            # Create services
            content_repo = ContentRepository(session)
            trivia_client = TriviaAPIClient()
            content_service = ContentService(content_repo, trivia_client, settings)
            
            # Populate questions for existing dungeons only (not the new ones yet)
            categories = ["sports", "music", "history", "pop_culture"]
            
            total_added = 0
            for category in categories:
                print(f"\n{'='*60}")
                print(f"Populating {category.upper()} category...")
                print(f"{'='*60}")
                
                added = await content_service.refresh_question_pool(
                    category=category,
                    batch_size=30,  # 30 per difficulty = 90 total per category
                    difficulty=None,
                    session=session
                )
                total_added += added
                print(f"✓ Added {added} questions for {category}")
            
            await session.commit()
            
            print("\n" + "=" * 60)
            print(f"✅ SUCCESS! Added {total_added} correctly categorized questions")
            print("=" * 60)
            print("\nNow each dungeon will have questions matching its category!")
            print("Test your game - Music dungeon should only have music questions!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(clear_and_repopulate())

