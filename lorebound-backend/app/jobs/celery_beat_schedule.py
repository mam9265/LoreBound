"""Celery Beat periodic task schedule configuration."""

from celery.schedules import crontab

# Periodic task schedule
beat_schedule = {
    # Seed questions every 5 minutes
    'seed-questions-every-5-minutes': {
        'task': 'app.jobs.tasks.daily_tasks.refresh_question_pool',
        'schedule': 300.0,  # Every 5 minutes (in seconds)
        'kwargs': {
            'category': None,  # All categories
            'batch_size': 10,  # Small batches to respect rate limiting
        },
        'options': {
            'expires': 240,  # Task expires after 4 minutes if not picked up
        }
    },
    
    # Generate daily challenge at midnight UTC
    'generate-daily-challenge': {
        'task': 'app.jobs.tasks.daily_tasks.generate_daily_challenge',
        'schedule': crontab(hour=0, minute=1),  # 12:01 AM UTC daily
        'options': {
            'expires': 3600,  # Task expires after 1 hour
        }
    },
}

