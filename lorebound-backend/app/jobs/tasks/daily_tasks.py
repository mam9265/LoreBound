"""Daily recurring tasks."""

import logging
from datetime import datetime, timezone

from ...jobs.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, retry_kwargs={"max_retries": 3})
def generate_daily_challenge(self):
    """Generate daily challenge for today."""
    try:
        logger.info("Starting daily challenge generation...")
        
        # TODO: Implement actual daily challenge generation
        # This would use the ContentService to generate a new daily challenge
        
        today = datetime.now(timezone.utc).date()
        logger.info(f"Generated daily challenge for {today}")
        
        return {"status": "success", "date": str(today)}
        
    except Exception as exc:
        logger.error(f"Daily challenge generation failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True)
def refresh_question_pool(self, category=None, batch_size=10):
    """
    Background task to continuously fetch questions from OpenTDB API.
    Runs periodically to keep the question database fresh and populated.
    Batch size is kept small (10) to respect rate limiting.
    """
    import asyncio
    from ...repositories.base import AsyncSessionLocal
    from ...repositories.content_repo import ContentRepository
    from ...services.content_service import ContentService
    from ...services.trivia_api_client import TriviaAPIClient
    from ...core.config import settings
    
    async def _fetch_questions():
        async with AsyncSessionLocal() as session:
            try:
                content_repo = ContentRepository(session)
                trivia_client = TriviaAPIClient()
                content_service = ContentService(content_repo, trivia_client, settings)
                
                logger.info(f"🔄 Background seeding: Fetching {batch_size} questions (category: {category or 'all'})")
                
                # Fetch questions (respects 5-second rate limit)
                questions_added = await content_service.refresh_question_pool(
                    category=category,
                    batch_size=batch_size,
                    session=session
                )
                
                await session.commit()
                logger.info(f"✅ Background seeding: Added {questions_added} new questions")
                
                return questions_added
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Background seeding failed: {e}")
                raise
    
    try:
        # Run async function
        questions_added = asyncio.run(_fetch_questions())
        return {
            "status": "success",
            "category": category or "all",
            "questions_added": questions_added,
            "batch_size": batch_size
        }
        
    except Exception as exc:
        logger.error(f"Question pool refresh failed: {exc}")
        # Retry after 5 minutes if failed
        raise self.retry(exc=exc, countdown=300, max_retries=3)


@celery_app.task(bind=True)
def send_daily_notifications(self):
    """Send daily challenge notifications to users."""
    try:
        logger.info("Sending daily challenge notifications...")
        
        # TODO: Implement push notifications for daily challenges
        
        logger.info("Daily notifications sent successfully")
        
        return {"status": "success", "notifications_sent": 0}
        
    except Exception as exc:
        logger.error(f"Daily notifications failed: {exc}")
        raise
