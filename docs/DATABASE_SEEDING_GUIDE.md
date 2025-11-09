# Database Seeding Guide - Trivia Questions

Complete guide to populate your LoreBound database with trivia questions from the OpenTDB API.

---

## 🎯 Overview

LoreBound fetches trivia questions from **OpenTDB (Open Trivia Database)** - a free, crowd-sourced trivia API. This guide shows you how to seed your database with questions.

**Important**: OpenTDB has a rate limit of **1 request per 5 seconds per IP address**. The scripts automatically respect this limit.

---

## 📋 Prerequisites

Before starting, make sure:

1. ✅ Backend services are running
2. ✅ Database is up and migrations are complete
3. ✅ You're in the `lorebound-backend` directory

### Quick Check

```bash
cd lorebound-backend

# Check services are running
docker-compose ps

# Should show:
# api    - Up
# db     - Up  
# redis  - Up
# worker - Up
# beat   - Up
```

If services aren't running:
```bash
docker-compose up -d
```

---

## 🚀 Method 1: Quick Seeding (Recommended for Testing)

**Use this for**: Quick testing, getting started, seeding one category

### Step 1: Run the populate script

```bash
# From lorebound-backend directory
docker-compose exec api python -m scripts.populate_questions
```

This will:
- Fetch 50 questions for each category (history, music, sports, etc.)
- Fetch questions across all difficulty levels (easy, medium, hard)
- Respect OpenTDB's 1 request per 5 seconds rate limit
- Show progress as it runs

**Expected output:**
```
============================================================
Starting question population
Category: all, Questions per category: 50
Note: OpenTDB rate limit is 1 request per 5 seconds
This will take time to respect the rate limit...
============================================================
Questions before: 12
Fetching questions for category: history
Rate limiting: waiting 4.85s before next OpenTDB request
Fetching questions for category: music
Rate limiting: waiting 4.92s before next OpenTDB request
...
Questions after: 162
Total questions added: 150
✅ Successfully populated questions!
```

**Time estimate**: ~3-5 minutes for 50 questions per category

---

## 🎓 Method 2: Seed Specific Category

**Use this for**: Focusing on one category, fixing low question counts

### Seed One Category

```bash
# History questions
docker-compose exec api python -m scripts.populate_questions --category history --count 100

# Music questions
docker-compose exec api python -m scripts.populate_questions --category music --count 100

# Sports questions
docker-compose exec api python -m scripts.populate_questions --category sports --count 50

# Pop culture questions  
docker-compose exec api python -m scripts.populate_questions --category pop_culture --count 75
```

### Available Categories

```
- history
- music
- sports
- pop_culture
- science
- geography
- film
- television
- video_games
- books
- art
- nature
```

**Time estimate**: ~1-2 minutes per 20 questions (due to rate limiting)

---

## 🏭 Method 3: Production Seeding (Large Database)

**Use this for**: Production deployment, complete database

### Step 1: Run large batch seeding

```bash
# Seed 200 questions per category (recommended for production)
docker-compose exec api python -m scripts.populate_questions --count 200
```

**Expected results:**
- ~800-1200 total questions
- Good variety across all categories
- All difficulty levels covered

**Time estimate**: ~10-15 minutes (due to rate limiting)

### Step 2: Verify the results

```bash
# Connect to database
docker-compose exec db psql -U postgres -d lorebound

# Check question counts
SELECT 
    d.category, 
    q.difficulty,
    COUNT(*) as question_count
FROM questions q
JOIN dungeons d ON q.dungeon_id = d.id
GROUP BY d.category, q.difficulty
ORDER BY d.category, q.difficulty;

# Exit
\q
```

**Expected output:**
```
  category   | difficulty | question_count
-------------+------------+---------------
 history     | easy       |           60
 history     | medium     |           70
 history     | hard       |           70
 music       | easy       |           55
 music       | medium     |           65
 music       | hard       |           60
 sports      | easy       |           50
 ...
```

---

## 🔄 Method 4: Automatic Background Seeding

**Use this for**: Keeping questions fresh automatically

The backend has a **Celery Beat scheduler** that automatically seeds questions every day.

### Check if automatic seeding is running

```bash
# View beat scheduler logs
docker-compose logs -f beat

# Should see:
# beat: Starting...
# Scheduler: Sending due task refresh-question-pool-task
```

### Trigger manual background seeding

```bash
# From lorebound-backend directory
docker-compose exec api python -m scripts.trigger_seeding
```

This uses the Celery worker to seed in the background.

---

## 🔍 Verify Questions Are Seeded

### Method A: Check Database Directly

```bash
# Connect to database
docker-compose exec db psql -U postgres -d lorebound

# Count total questions
SELECT COUNT(*) as total_questions FROM questions;

# Count by difficulty
SELECT difficulty, COUNT(*) as count 
FROM questions 
GROUP BY difficulty;

# Count by category
SELECT d.category, COUNT(q.id) as count
FROM questions q
JOIN dungeons d ON q.dungeon_id = d.id
GROUP BY d.category
ORDER BY count DESC;

# Exit
\q
```

### Method B: Check via API

```bash
# Get your access token first
TOKEN="your_access_token_here"

# Check a dungeon's questions
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/v1/content/dungeons"

# Get questions for a specific dungeon
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/v1/content/questions?dungeon_id=YOUR_DUNGEON_ID&floor=1&count=10"
```

### Method C: Test in Mobile App

1. Open the LoreBound app
2. Go to **Dungeon Select**
3. Select any dungeon
4. Start playing
5. **Check**: Questions should load and display properly

---

## 📊 Recommended Question Counts

### Minimum (for testing):
- **50 questions per category**
- **Total: ~200 questions**
- Sufficient for basic testing

### Recommended (for development):
- **100 questions per category**
- **Total: ~400-600 questions**
- Good variety for development

### Production:
- **200+ questions per category**
- **Total: 800-1200 questions**
- Ensures players don't see repeats frequently

---

## 🐛 Troubleshooting

### Issue 1: "Network request failed" or timeout

**Problem**: Can't connect to OpenTDB API

**Solution**:
```bash
# Test API connection
docker-compose exec api python -m scripts.check_api_status

# Check if OpenTDB is accessible
curl "https://opentdb.com/api.php?amount=1&type=multiple"
```

### Issue 2: "Rate limit exceeded"

**Problem**: Making requests too fast

**Solution**: The scripts automatically handle this! Just wait. OpenTDB allows only 1 request per 5 seconds.

### Issue 3: Very few questions added

**Problem**: Questions might already exist (duplicates are skipped)

**Check**:
```bash
# Check current question count
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions;"

# Check by source
docker-compose exec db psql -U postgres -d lorebound -c "SELECT metadata->>'api_provider' as source, COUNT(*) FROM questions GROUP BY source;"
```

### Issue 4: Daily challenge only shows 2 questions

**Problem**: Not enough HARD difficulty questions

**Solution**:
```bash
# Seed more hard questions specifically
docker-compose exec api python -m scripts.populate_questions --count 150

# Then check hard question counts
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions WHERE difficulty = 'hard';"
```

**You need**: At least 10 hard questions per category for daily challenges.

### Issue 5: Script hangs or is very slow

**Expected**: This is normal! OpenTDB rate limit means 1 request per 5 seconds.

**Example timings**:
- 10 questions = ~50 seconds
- 50 questions = ~4 minutes  
- 100 questions = ~8 minutes
- 200 questions = ~15 minutes

Just let it run! The script will show progress.

---

## 🧪 Test Seeding Script

Quick test to verify everything works:

```bash
# Quick test - fetch just 10 questions
docker-compose exec api python -m scripts.populate_questions --category music --count 10

# Check the results
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions WHERE dungeon_id IN (SELECT id FROM dungeons WHERE category = 'music');"
```

Should add ~10 new music questions in ~1 minute.

---

## 📝 Understanding the Process

### How Seeding Works

1. **Script connects** to the database
2. **Checks existing questions** (to avoid duplicates)
3. **Calls OpenTDB API** for new questions
   - Respects 5-second rate limit
   - Fetches questions by category and difficulty
4. **Parses and stores** questions in database
   - Decodes HTML entities
   - Shuffles answer choices
   - Stores correct answer index
5. **Shows progress** and final stats

### OpenTDB API Request Format

```
https://opentdb.com/api.php?
  amount=10                    # Number of questions
  &category=23                 # Category ID (23 = History)
  &difficulty=hard             # easy, medium, or hard
  &type=multiple               # Multiple choice
```

### What Gets Stored

For each question:
- ✅ Question text (HTML decoded)
- ✅ 4 answer choices (shuffled)
- ✅ Correct answer index
- ✅ Category (mapped to dungeon)
- ✅ Difficulty (easy/medium/hard)
- ✅ Source metadata (OpenTDB ID)

---

## 🎯 Quick Reference

### Most Common Commands

```bash
# Quick seed (50 questions per category)
docker-compose exec api python -m scripts.populate_questions

# Seed specific category
docker-compose exec api python -m scripts.populate_questions --category history --count 100

# Large production seed
docker-compose exec api python -m scripts.populate_questions --count 200

# Check question count
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions;"

# Check by difficulty
docker-compose exec db psql -U postgres -d lorebound -c "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty;"

# View logs
docker-compose logs -f api
```

---

## 🚨 Important Notes

### OpenTDB Rate Limiting
- **Limit**: 1 request per 5 seconds per IP
- **Why**: Prevents abuse of the free API
- **Our scripts**: Automatically respect this limit
- **Be patient**: Seeding takes time!

### Question Duplicates
- Scripts automatically skip duplicate questions
- Duplicates are detected by question text hash
- If few questions are added, you might already have them

### API Availability
- OpenTDB is a free service
- Occasionally may be down for maintenance
- If seeding fails, try again later
- Check status: https://opentdb.com/

### Database Persistence
- Questions are stored permanently in PostgreSQL
- Survive container restarts
- Only lost if database volume is deleted

---

## ✅ Success Checklist

After seeding, verify:

- [ ] Total questions > 200
- [ ] Questions in all categories (history, music, sports, etc.)
- [ ] Questions in all difficulties (easy, medium, hard)
- [ ] Hard questions > 50 (needed for daily challenges)
- [ ] Mobile app can load and display questions
- [ ] No errors in API logs

---

## 📚 Additional Resources

### Scripts Location
- `lorebound-backend/scripts/populate_questions.py` - Main seeding script
- `lorebound-backend/scripts/seed_once.py` - Quick one-time seed
- `lorebound-backend/scripts/trigger_seeding.py` - Trigger background job
- `lorebound-backend/scripts/check_api_status.py` - Test API connection

### Related Documentation
- `archive/DAILY_CHALLENGE_FIX_GUIDE.md` - Fix daily challenge issues
- `archive/BACKGROUND_SEEDING_COMPLETE.md` - Background seeding info
- `TODAYS_CHANGES_SUMMARY.md` - Complete changes overview

### OpenTDB Documentation
- Website: https://opentdb.com/
- API Docs: https://opentdb.com/api_config.php
- Category List: https://opentdb.com/api_category.php

---

## 🎉 You're Done!

Your database should now be seeded with trivia questions! Players can enjoy varied questions across all dungeons and difficulty levels.

**Next steps**:
1. Test the mobile app
2. Try a daily challenge
3. Check question variety in different dungeons
4. Set up automatic background seeding

**Questions?** Check the logs:
```bash
docker-compose logs -f api | grep "question"
```

---

**Last Updated**: November 2, 2025  
**Status**: Ready to Use ✅

