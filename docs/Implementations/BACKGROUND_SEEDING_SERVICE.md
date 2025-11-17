# Background Question Seeding Service 🤖

## Overview

I've implemented a **background service** that continuously fetches questions from OpenTDB API and populates your database. This runs automatically in the background, perfect for your VPS deployment!

## Implementation

### Architecture

```
┌─────────────┐
│   Celery    │  ← Scheduler (every 5 minutes)
│    Beat     │
└──────┬──────┘
       │ Triggers
       ▼
┌─────────────┐
│   Celery    │  ← Executes task
│   Worker    │
└──────┬──────┘
       │ Fetches
       ▼
┌─────────────┐
│   OpenTDB   │  ← External API (rate limited: 1 req/5s)
│     API     │
└──────┬──────┘
       │ Stores
       ▼
┌─────────────┐
│  PostgreSQL │  ← Questions database
│  Database   │
└─────────────┘
```

### Components

1. **Celery Beat** - Scheduler that triggers tasks
2. **Celery Worker** - Executes the seeding tasks
3. **Background Task** - Fetches and stores questions

## Configuration

### Task Schedule

The seeding task runs **every 5 minutes**:

```python
"seed-questions-every-5-minutes": {
    "task": "app.jobs.tasks.daily_tasks.refresh_question_pool",
    "schedule": 300.0,  # Every 5 minutes
    "kwargs": {
        "batch_size": 10,  # 10 questions per run
    }
}
```

### What It Does

**Every 5 minutes**:
1. Wakes up automatically
2. Fetches 10 questions from OpenTDB
3. Respects 5-second rate limit between requests  
4. Stores questions in database
5. Logs progress
6. Goes back to sleep

**Math**:
- 10 questions per 5 minutes
- = 120 questions per hour
- = **2,880 questions per day** (if API allows)

## Services Running

```bash
docker-compose ps
```

You should see **5 services**:
- ✅ `api` - FastAPI backend
- ✅ `db` - PostgreSQL database
- ✅ `redis` - Redis cache
- ✅ `worker` - Celery worker (executes tasks)
- ✅ `beat` - Celery beat (scheduler) **← NEW!**

## Monitoring

### Check Beat Scheduler Status

```bash
docker-compose logs -f beat
```

You'll see:
```
celery beat v5.5.3 is starting.
beat: Starting...
Scheduler: Sending due task seed-questions-every-5-minutes
```

### Check Worker Processing

```bash
docker-compose logs -f worker
```

You'll see:
```
Task app.jobs.tasks.daily_tasks.refresh_question_pool[...] received
🔄 Background seeding: Fetching 10 questions (category: all)
✅ Background seeding: Added 8 new questions
Task app.jobs.tasks.daily_tasks.refresh_question_pool[...] succeeded
```

### Monitor Question Growth

```bash
# Watch questions increase over time
docker-compose exec -T db psql -U postgres -d lorebound -c \
  "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty;"
```

Run this every few minutes and you'll see the counts growing!

## VPS Deployment

### Production Setup

When deploying to your VPS:

**1. Start all services:**
```bash
docker-compose up -d
```

**2. Verify all 5 containers are running:**
```bash
docker-compose ps
```

**3. Check beat scheduler:**
```bash
docker-compose logs beat | tail -20
```

**4. Monitor worker:**
```bash
docker-compose logs -f worker
```

### Background Seeding Benefits

✅ **Automatic** - No manual intervention needed  
✅ **Continuous** - Runs 24/7 on VPS  
✅ **Rate Limited** - Respects API limits (no blocking)  
✅ **Resilient** - Retries on failure  
✅ **Scalable** - Handles multiple categories  

### Expected Behavior

**First Hour**:
- Starts with ~205 questions
- Adds ~120 new questions (12 runs × 10 questions)
- Total: ~325 questions

**After 24 Hours**:
- Could have 2,000+ questions (if API allows)
- Excellent variety for all users
- All categories well-stocked

**Ongoing**:
- Maintains fresh question pool
- Automatically fills gaps
- Ensures variety for players

## Task Configuration

### Modify Schedule

To change how often it runs, edit `app/jobs/worker.py`:

```python
"seed-questions-every-5-minutes": {
    "schedule": 300.0,  # Change this (seconds)
    # 60 = 1 minute
    # 300 = 5 minutes (current)
    # 600 = 10 minutes
    # 3600 = 1 hour
}
```

### Modify Batch Size

To fetch more/less questions per run:

```python
"seed-questions-every-5-minutes": {
    "kwargs": {
        "batch_size": 10,  # Change this
        # 5 = 5 questions per run (safer)
        # 10 = 10 questions per run (current)
        # 20 = 20 questions per run (more aggressive)
    }
}
```

### Target Specific Category

To focus on one category:

```python
"seed-questions-every-5-minutes": {
    "kwargs": {
        "category": "sports",  # music, history, sports, pop_culture, science
        "batch_size": 10,
    }
}
```

## Testing

### Manual Trigger

You can manually trigger the seeding task:

```bash
docker-compose exec worker poetry run python -c "
from app.jobs.tasks.daily_tasks import refresh_question_pool
result = refresh_question_pool.delay()
print(f'Task ID: {result.id}')
"
```

### Check Task Results

```bash
# Monitor worker logs in real-time
docker-compose logs -f worker

# Check last 50 lines
docker-compose logs --tail 50 worker
```

### Verify Questions Are Being Added

```bash
# Before
docker-compose exec -T db psql -U postgres -d lorebound -c \
  "SELECT COUNT(*) as total FROM questions;"

# Wait 5-10 minutes

# After
docker-compose exec -T db psql -U postgres -d lorebound -c \
  "SELECT COUNT(*) as total FROM questions;"

# Count should increase!
```

## Troubleshooting

### Beat Scheduler Not Running

```bash
# Check status
docker-compose ps beat

# If not running
docker-compose up -d beat

# Check logs for errors
docker-compose logs beat
```

### Worker Not Processing Tasks

```bash
# Restart worker
docker-compose restart worker

# Check if connected to Redis
docker-compose logs worker | grep -i connected
```

### No Questions Being Added

Possible causes:
1. **Rate limiting** - OpenTDB limits (expected, task retries)
2. **Duplicate questions** - Already have those questions
3. **API down** - Temporary outage (task retries automatically)

Check worker logs:
```bash
docker-compose logs worker | grep -i "added\|failed\|error"
```

### Stop Background Seeding

If you want to stop it temporarily:

```bash
# Stop beat scheduler
docker-compose stop beat

# To restart
docker-compose start beat
```

## Production Recommendations

### For VPS Deployment

**Recommended Settings**:
```python
# Every 10 minutes (less aggressive)
"schedule": 600.0,  

# Small batch size (respect rate limits)
"batch_size": 5,

# Focus on categories you need
"category": None,  # or specific category
```

**Resource Usage**:
- Beat: ~20MB RAM
- Worker: ~100MB RAM  
- Minimal CPU (mostly waiting)

### Monitoring On VPS

Add monitoring for:
- Docker container health
- Question count growth
- Task success/failure rates
- API rate limit violations

Example monitoring command:
```bash
# Add to cron every hour
0 * * * * docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c \
  "SELECT COUNT(*) FROM questions;" >> /var/log/question_count.log
```

## Summary

✅ **Background seeding service implemented!**

Services running:
- ✅ API (FastAPI)
- ✅ Database (PostgreSQL)  
- ✅ Cache (Redis)
- ✅ Worker (Celery)
- ✅ **Beat (Celery Scheduler)** ← NEW!

What it does:
- 🤖 Runs automatically every 5 minutes
- 📥 Fetches 10 questions from OpenTDB
- 💾 Stores them in database
- ♻️ Repeats forever
- 🚀 Perfect for VPS deployment!

Your database will continuously grow with fresh questions, ensuring variety for all players! 🎮

---

**Next**: Wait 5 minutes and check the logs to see the first seeding run!

```bash
docker-compose logs -f worker
```

