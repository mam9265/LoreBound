# Daily Challenge Issue - Fix Guide

## Problem Summary
The daily challenge only gives 2 questions instead of 10, and the last answer is treated as incorrect.

## Root Cause
The backend tries to fetch 10 **HARD** difficulty questions for the daily challenge, but there are likely only 2 hard questions available in the database for that specific category. The API supplementation feature that should fetch more questions isn't working properly.

---

## Quick Fix Option 1: Populate More Hard Questions ⭐ RECOMMENDED

### Step 1: Check Backend Logs
```bash
cd lorebound-backend
docker-compose logs -f api
```

Look for messages like:
```
Insufficient hard questions (2/10) for dungeon...
```

This confirms the issue.

### Step 2: Run the Population Script
We have a script that populates questions from the OpenTDB API:

```bash
# From the lorebound-backend directory
docker-compose exec api python -m scripts.populate_questions
```

This will fetch questions from the API and populate your database with more hard questions.

### Step 3: Verify Question Count
Check if you now have more hard questions:

```bash
# Connect to the database
docker-compose exec db psql -U postgres -d lorebound

# Check hard questions per category
SELECT d.category, COUNT(*) as hard_questions
FROM questions q
JOIN dungeons d ON q.dungeon_id = d.id
WHERE q.difficulty = 'hard'
GROUP BY d.category;

# Exit
\q
```

You should see at least 10 hard questions per category.

---

## Quick Fix Option 2: Trigger Background Seeding

The backend has a background job that should automatically fetch questions:

```bash
# Trigger the seeding task manually
docker-compose exec api python -m scripts.trigger_seeding

# Or use seed_once
docker-compose exec api python -m scripts.seed_once
```

---

## Quick Fix Option 3: Restart Services

Sometimes the Celery Beat scheduler needs a restart:

```bash
cd lorebound-backend
docker-compose restart beat worker
docker-compose logs -f beat
```

You should see:
```
beat: Starting...
Scheduler: Sending due task daily-challenge-task
```

---

## Understanding the Issue

### How Daily Challenge Works

1. **Backend generates challenge**: Uses `_generate_daily_challenge()` in `content_service.py`
2. **Fetches hard questions**: Tries to get 10 HARD difficulty questions
3. **Falls back to API**: If insufficient questions, calls `_supplement_questions_from_api()`
4. **Problem**: The API supplementation might fail silently, returning only what's available (2 questions)

### Code Location
```python
# File: lorebound-backend/app/services/content_service.py
# Line: 192-201

if len(hard_questions) < question_count:
    logger.warning(f"Insufficient hard questions ({len(hard_questions)}/{question_count})")
    # Try to fetch more hard questions from API
    hard_questions = await self._supplement_questions_from_api(
        category=dungeon.category,
        floor=10,  # Floor 10 = hard difficulty
        count=question_count,
        existing_questions=hard_questions,
        session=session
    )
```

---

## Fixing "Last Answer Treated as Incorrect"

This is a separate issue with answer validation. The problem is likely in the frontend logic.

### Check RunGameplay.js

The issue might be in how the last question is handled when the game ends. Look at:

```javascript
// File: lorebound/src/screens/RunGameplay.js
// Line: 121-179

const handleAnswerSubmit = async (answerIndex = selectedAnswer, timedOut = false) => {
  // Validation happens here
  const validation = await RunService.validateAnswer(
    runData.id,
    question.id,
    answerIndex
  );
  isCorrect = validation.is_correct;
}
```

### Possible Issue
The last question might be ending the game before validation completes. Check if:
1. Lives reach 0 before validation
2. Navigation away from screen interrupts validation
3. The submit endpoint is being called properly

---

## Recommended Solution Steps

### For Your Partner:

**Tell him to run these commands in order:**

1. **First, check the logs to confirm the issue:**
   ```bash
   cd lorebound-backend
   docker-compose logs -f api | grep "hard questions"
   ```

2. **Populate more questions:**
   ```bash
   docker-compose exec api python -m scripts.populate_questions
   ```
   
   This will take a few minutes and should output:
   ```
   Fetching questions for category: history
   Added 50 new questions
   Fetching questions for category: science
   ...
   ```

3. **Verify the fix:**
   ```bash
   docker-compose exec db psql -U postgres -d lorebound -c "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty;"
   ```
   
   Should show:
   ```
   difficulty | count
   -----------+-------
   easy       |   90+
   medium     |   90+
   hard       |   60+
   ```

4. **Restart the app and try daily challenge again:**
   - Close the mobile app completely
   - Reopen and try daily challenge
   - Should now show all 10 questions

---

## If Still Having Issues

### Enable Debug Logging

Add this to see what's happening:

```bash
# Check API logs in real-time
docker-compose logs -f api

# In another terminal, try the daily challenge
# You'll see logs like:
# "Getting questions for daily challenge..."
# "Selected X hard questions for daily challenge"
```

### Manual Database Check

```bash
# Connect to database
docker-compose exec db psql -U postgres -d lorebound

# Check today's daily challenge
SELECT dc.id, dc.date, dc.seed, d.category, dc.modifiers
FROM daily_challenges dc
JOIN dungeons d ON dc.dungeon_id = d.id
WHERE DATE(dc.date) = CURRENT_DATE;

# Check hard questions for that category
SELECT COUNT(*) 
FROM questions q
JOIN dungeons d ON q.dungeon_id = d.id
WHERE d.category = 'history'  -- Replace with actual category
AND q.difficulty = 'hard';
```

### Test Daily Challenge Endpoint Directly

```bash
# Get your auth token first (from mobile app network inspector)
TOKEN="your_token_here"

# Test daily challenge endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/v1/content/daily

# Test questions endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/v1/content/daily/{challenge_id}/questions
```

---

## Prevention - Automatic Background Seeding

Make sure these services are running:

```bash
docker-compose ps
```

Should show:
- ✅ api (running)
- ✅ db (running)
- ✅ redis (running)
- ✅ worker (running)
- ✅ beat (running)  ← This one is important!

The `beat` service automatically:
- Generates daily challenges at midnight
- Populates questions throughout the day
- Keeps the question pool fresh

If `beat` is not running:
```bash
docker-compose up -d beat
docker-compose logs -f beat
```

---

## Summary for Your Partner

**Quick Fix (Run these 3 commands):**

```bash
cd lorebound-backend
docker-compose exec api python -m scripts.populate_questions
docker-compose restart api
```

Then try the daily challenge again - should now have 10 questions!

---

**Need More Help?**

Check these files:
- Backend logs: `docker-compose logs -f api`
- Celery worker: `docker-compose logs -f worker`
- Celery beat: `docker-compose logs -f beat`
- Database: `docker-compose exec db psql -U postgres -d lorebound`

The issue is definitely that there aren't enough hard questions in the database for the selected category. The population script will fix it!

