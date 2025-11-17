"""Manually trigger the background seeding task."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.jobs.tasks.daily_tasks import refresh_question_pool

if __name__ == "__main__":
    print("Triggering background seeding task...")
    print("Category: sports")
    print("Batch size: 15")
    print()
    
    # Trigger the task
    result = refresh_question_pool.apply_async(
        kwargs={'category': 'sports', 'batch_size': 15}
    )
    
    print(f"✅ Task queued successfully!")
    print(f"Task ID: {result.id}")
    print()
    print("Monitor progress with:")
    print("  docker-compose logs -f worker")
    print()
    print("Check result:")
    print(f"  result = refresh_question_pool.AsyncResult('{result.id}')")
    print(f"  result.ready()  # True if complete")
    print(f"  result.result   # Get result")

