"""
Script to populate the database with questions from external trivia APIs.
Run this to add many questions so players get variety.

Usage:
    python -m scripts.populate_questions
    python -m scripts.populate_questions --category music --count 100
"""

import asyncio
import sys
import argparse
from pathlib import Path


from app.repositories.base import AsyncSessionLocal
from app.repositories.content_repo import ContentRepository
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient
from app.core.config import settings
from app.core.logging import get_logger
from app.domain.enums import DungeonCategory, QuestionDifficulty

logger = get_logger(__name__)


async def populate_questions(category: str = None, questions_per_category: int = 100, difficulty: str = None):
    """
    Populate database with questions from external trivia API.
    
    Args:
        category: Optional specific category to populate (music, history, etc.)
        questions_per_category: Number of questions to fetch per category/difficulty combo
        difficulty: Optional specific difficulty to populate (easy, medium, hard)
    
    Note: OpenTDB has a rate limit of 1 request per 5 seconds per IP.
          This script respects that limit and will pace requests accordingly.
    """
    logger.info("="*60)
    logger.info("Starting question population")
    logger.info(f"Category: {category or 'all'}, Difficulty: {difficulty or 'all'}, Questions per combo: {questions_per_category}")
    logger.info("Note: OpenTDB rate limit is 1 request per 5 seconds")
    logger.info("This will take time to respect the rate limit...")
    logger.info("="*60)
    
    async with AsyncSessionLocal() as session:
        # Create repositories and services
        content_repo = ContentRepository(session)
        trivia_client = TriviaAPIClient()
        content_service = ContentService(content_repo, trivia_client, settings)
        
        try:
            # Get initial stats
            stats_before = await content_repo.get_content_stats()
            logger.info(f"Questions before: {stats_before['total_questions']}")
            
            # Refresh question pool
            total_added = await content_service.refresh_question_pool(
                category=category,
                batch_size=questions_per_category,
                difficulty=difficulty,
                session=session
            )
            
            # Get final stats
            stats_after = await content_repo.get_content_stats()
            logger.info(f"Questions after: {stats_after['total_questions']}")
            logger.info(f"Total questions added: {total_added}")
            
            # Show breakdown by category and difficulty
            logger.info("\nQuestions by difficulty:")
            for difficulty, count in stats_after['questions_by_difficulty'].items():
                logger.info(f"  {difficulty}: {count}")
            
            await session.commit()
            logger.info("✅ Successfully populated questions!")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Failed to populate questions: {e}")
            raise


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Populate database with trivia questions from external APIs"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=[cat.value for cat in DungeonCategory],
        help="Specific category to populate (music, history, etc.)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of questions to fetch per category/difficulty combo (default: 50)"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=[d.value for d in QuestionDifficulty],
        help="Specific difficulty to populate (easy, medium, hard). If not provided, fetches all difficulties."
    )
    
    args = parser.parse_args()
    
    try:
        await populate_questions(
            category=args.category,
            questions_per_category=args.count,
            difficulty=args.difficulty
        )
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

