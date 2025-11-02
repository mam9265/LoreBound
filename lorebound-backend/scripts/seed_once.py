"""Quick one-time seeding script."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.jobs.tasks.daily_tasks import refresh_question_pool

print("🔄 Seeding sports questions...")
result = refresh_question_pool(category='sports', batch_size=10)
print(f"✅ Added: {result['questions_added']} questions")
print(f"Category: {result['category']}")

