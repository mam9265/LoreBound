"""Test daily challenge generation and retrieval."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.repositories.base import AsyncSessionLocal
from app.repositories.content_repo import ContentRepository
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient
from app.core.config import settings
from app.core.logging import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)

async def test_daily_challenge():
    """Test daily challenge generation."""
    async with AsyncSessionLocal() as session:
        try:
            # Create services
            content_repo = ContentRepository(session)
            trivia_client = TriviaAPIClient()
            content_service = ContentService(content_repo, trivia_client, settings)
            
            logger.info("Testing daily challenge generation...")
            
            # Get or generate today's challenge
            challenge = await content_service.get_daily_challenge(session)
            
            logger.info(f"✅ Daily Challenge Retrieved!")
            logger.info(f"  ID: {challenge.id}")
            logger.info(f"  Dungeon: {challenge.dungeon.title if hasattr(challenge, 'dungeon') else 'N/A'}")
            logger.info(f"  Category: {challenge.dungeon.category if hasattr(challenge, 'dungeon') else 'N/A'}")
            logger.info(f"  Seed: {challenge.seed}")
            logger.info(f"  Date: {challenge.date}")
            logger.info(f"  Expires: {challenge.expires_at}")
            logger.info(f"  Modifiers: {challenge.modifiers}")
            
            # Get questions for the challenge
            logger.info("\nFetching challenge questions...")
            from uuid import uuid4
            questions = await content_service.get_daily_challenge_questions(
                challenge_id=challenge.id,
                user_id=uuid4(),  # Dummy user ID
                session=session
            )
            
            logger.info(f"✅ Got {len(questions)} questions")
            if questions:
                logger.info(f"  Sample question: {questions[0].prompt[:60]}...")
                logger.info(f"  Difficulty: {questions[0].difficulty}")
            
            await session.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False

if __name__ == "__main__":
    print("="*60)
    print("Daily Challenge Test")
    print("="*60)
    success = asyncio.run(test_daily_challenge())
    print("="*60)
    sys.exit(0 if success else 1)

