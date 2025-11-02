"""
Test script to verify question variety across multiple runs.
This script will request questions multiple times and check for variety.

Usage:
    python -m scripts.test_question_variety
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.repositories.base import AsyncSessionLocal
from app.repositories.content_repo import ContentRepository
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient
from app.core.config import settings
from app.core.logging import get_logger
from app.domain.enums import DungeonCategory
from uuid import UUID, uuid4

logger = get_logger(__name__)


async def test_question_variety():
    """Test that questions vary across multiple requests."""
    logger.info("Testing question variety across multiple requests...")
    
    async with AsyncSessionLocal() as session:
        # Create services
        content_repo = ContentRepository(session)
        trivia_client = TriviaAPIClient()
        content_service = ContentService(content_repo, trivia_client, settings)
        
        try:
            # Get all dungeons
            dungeons = await content_repo.get_all_dungeons()
            if not dungeons:
                logger.error("No dungeons found! Please seed the database first.")
                return False
            
            # Pick first dungeon
            dungeon = dungeons[0]
            logger.info(f"Testing with dungeon: {dungeon.title} (category: {dungeon.category})")
            
            # Count available questions
            question_count = await content_repo.count_questions_by_dungeon(dungeon.id)
            logger.info(f"Available questions for this dungeon: {question_count}")
            
            if question_count < 20:
                logger.warning(f"⚠️  Only {question_count} questions available. Fetching more from API...")
                # Fetch more questions
                async with trivia_client:
                    from app.domain.enums import QuestionDifficulty
                    for difficulty in [QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM]:
                        try:
                            external_qs = await trivia_client.fetch_questions(
                                amount=30,
                                category=dungeon.category.value,
                                difficulty=difficulty,
                                provider=trivia_client.__class__.__dict__.get('TriviaAPIProvider', None) or None
                            )
                            logger.info(f"Fetched {len(external_qs)} {difficulty.value} questions from API")
                        except Exception as e:
                            logger.warning(f"Failed to fetch {difficulty} questions: {e}")
            
            # Request questions multiple times
            test_user_id = uuid4()
            num_requests = 3
            question_sets = []
            
            logger.info(f"\nRequesting questions {num_requests} times to check for variety...")
            
            for i in range(num_requests):
                questions = await content_service.get_questions_for_dungeon(
                    dungeon_id=dungeon.id,
                    floor=1,
                    count=5,
                    user_id=test_user_id,
                    session=session,
                    run_seed=None  # Let it generate random seed
                )
                
                question_ids = [str(q.id) for q in questions]
                question_texts = [q.prompt[:50] for q in questions]
                question_sets.append(set(question_ids))
                
                logger.info(f"\nRequest #{i+1}:")
                logger.info(f"  Got {len(questions)} questions")
                for j, text in enumerate(question_texts, 1):
                    logger.info(f"  {j}. {text}...")
            
            # Check for variety
            all_same = all(s == question_sets[0] for s in question_sets)
            
            if all_same:
                logger.error("\n❌ FAIL: All requests returned the same questions!")
                logger.error("This means question variety is not working.")
                return False
            else:
                # Calculate overlap
                overlaps = []
                for i in range(len(question_sets)-1):
                    overlap = len(question_sets[i] & question_sets[i+1])
                    overlaps.append(overlap)
                
                avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
                logger.info(f"\n✅ SUCCESS: Questions vary across requests!")
                logger.info(f"Average overlap between consecutive requests: {avg_overlap:.1f}/5 questions")
                logger.info(f"Variety rate: {((5-avg_overlap)/5)*100:.1f}%")
                return True
            
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("LoreBound Question Variety Test")
    logger.info("=" * 60)
    
    success = await test_question_variety()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ Test PASSED - Question variety is working!")
    else:
        logger.info("❌ Test FAILED - Questions are not varying")
        logger.info("\nTroubleshooting:")
        logger.info("1. Run: python -m scripts.populate_questions --count 100")
        logger.info("2. Make sure backend code changes are deployed")
        logger.info("3. Check logs for errors")
    logger.info("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

