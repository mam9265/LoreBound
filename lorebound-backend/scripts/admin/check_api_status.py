"""Quick check of external API status."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

async def check_api():
    """Check if external API is accessible."""
    async with TriviaAPIClient(timeout=5) as client:
        try:
            # Try to fetch just 1 question
            logger.info("Testing OpenTDB API with minimal request (1 question)...")
            questions = await client.fetch_questions(
                amount=1,
                difficulty=None,
                provider=TriviaAPIProvider.OPENTDB
            )
            
            if questions:
                logger.info(f"✅ SUCCESS! Fetched {len(questions)} question(s)")
                logger.info(f"Sample question: {questions[0].question[:80]}...")
                return True
            else:
                logger.warning("⚠️  API returned no questions")
                return False
                
        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            if "429" in str(e):
                logger.info("\n💡 OpenTDB is rate-limited. This is normal.")
                logger.info("   Rate limits usually clear in 5-10 minutes.")
                logger.info("   Your database already has 190 questions - plenty for variety!")
            return False

if __name__ == "__main__":
    print("="*60)
    print("OpenTDB API Status Check")
    print("="*60)
    success = asyncio.run(check_api())
    print("="*60)
    sys.exit(0 if success else 1)

