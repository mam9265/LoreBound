"""Celery worker configuration and task definitions."""

import logging
from celery import Celery
from ..core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "lorebound",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.jobs.tasks.daily_tasks",
        "app.jobs.tasks.leaderboard_tasks", 
        "app.jobs.tasks.analytics_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    result_expires=3600,  # 1 hour
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    worker_log_level="INFO",
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
)

# Configure task routing
celery_app.conf.task_routes = {
    "app.jobs.tasks.daily_tasks.*": {"queue": "daily"},
    "app.jobs.tasks.leaderboard_tasks.*": {"queue": "leaderboard"},
    "app.jobs.tasks.analytics_tasks.*": {"queue": "analytics"},
}

# Configure beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Seed questions every 5 minutes for continuous database population
    "seed-questions-every-5-minutes": {
        "task": "app.jobs.tasks.daily_tasks.refresh_question_pool",
        "schedule": 300.0,  # Every 5 minutes (in seconds)
        "kwargs": {
            "category": None,  # Rotate through all categories
            "batch_size": 10,  # Small batch to respect rate limiting
        },
        "options": {"queue": "daily"}
    },
    "generate-daily-challenge": {
        "task": "app.jobs.tasks.daily_tasks.generate_daily_challenge",
        "schedule": 60.0 * 60.0 * 24.0,  # Daily at midnight
        "options": {"queue": "daily"}
    },
    "update-leaderboards": {
        "task": "app.jobs.tasks.leaderboard_tasks.update_leaderboard_snapshots",
        "schedule": 60.0 * 15.0,  # Every 15 minutes
        "options": {"queue": "leaderboard"}
    },
    "cleanup-old-data": {
        "task": "app.jobs.tasks.analytics_tasks.cleanup_old_data",
        "schedule": 60.0 * 60.0,  # Hourly
        "options": {"queue": "analytics"}
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery worker."""
    print(f"Request: {self.request!r}")
    return "Debug task completed"

if __name__ == "__main__":
    celery_app.start()
