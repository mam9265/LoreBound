# 🎯 Question Variety Fix

## Problem

Geography dungeon shows the same questions every time because it only has 10 questions total, and each run requests 10 questions.

## Solution

Populate more questions for all new dungeons to provide variety!

---

## ✅ What I'm Doing Right Now

**Running in background:**
```bash
# Populating Geography questions (50 questions)
docker-compose exec api poetry run python scripts/populate_questions.py --category geography --count 50
```

This will take ~5-10 minutes due to OpenTDB rate limiting (1 request per 5 seconds).

---

## 📊 Current Question Counts

| Dungeon | Questions | Status |
|---------|-----------|--------|
| History | 90 | ✅ Good variety |
| Sports | 88 | ✅ Good variety |
| Music | 90 | ✅ Good variety |
| Pop Culture | 86 | ✅ Good variety |
| **Geography** | 10 → 50+ | 🔄 Populating |
| Books | 0 | ⏳ Needs population |
| Science | 0 | ⏳ Needs population |
| General | 0 | ⏳ Needs population |

---

## 🎮 Why More Questions = Better

### With 10 Questions:
```
Run 1: Questions 1-10 (all of them)
Run 2: Questions 1-10 (same, just shuffled)
Run 3: Questions 1-10 (same again)
```

### With 50+ Questions:
```
Run 1: Questions 3, 15, 42, 8, 31, 19, 5, 47, 12, 29
Run 2: Questions 18, 7, 44, 22, 39, 11, 48, 6, 33, 14
Run 3: Questions 25, 41, 9, 35, 2, 50, 16, 38, 21, 4
```

**Much more variety!** With 50 questions, you can play the dungeon 5+ times before repeating questions.

---

## 🚀 Next Steps to Populate All Dungeons

### Option 1: Let Current Process Finish
The geography population is running now. After it finishes, populate the others:

```bash
docker-compose exec api poetry run python scripts/populate_questions.py --category books --count 50
docker-compose exec api poetry run python scripts/populate_questions.py --category science --count 50
docker-compose exec api poetry run python scripts/populate_questions.py --category general --count 50
```

Each takes ~5-10 minutes.

### Option 2: Populate All at Once (Faster)
```bash
docker-compose exec api poetry run python scripts/populate_questions.py --count 30
```

This populates ALL categories at once (will skip categories that already have enough).

---

## ⚡ Quick Fix - Populate All New Dungeons

If you want to populate all 4 new dungeons quickly:

```bash
# Stop the current background process if you want
docker-compose exec api poetry run python -c "
import asyncio
from app.repositories.base import AsyncSessionLocal
from app.repositories.content_repo import ContentRepository
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient
from app.core.config import settings

async def quick_populate():
    async with AsyncSessionLocal() as session:
        repo = ContentRepository(session)
        client = TriviaAPIClient()
        service = ContentService(repo, client, settings)
        
        for category in ['geography', 'books', 'science', 'general']:
            print(f'Populating {category}...')
            await service.refresh_question_pool(
                category=category,
                batch_size=30,
                session=session
            )
        await session.commit()
        print('Done!')

asyncio.run(quick_populate())
"
```

---

## 🔧 How Question Selection Works

### Current Logic:

1. **Start run** → Generate unique seed (based on timestamp)
2. **Request questions** → Use seed to shuffle question pool
3. **Select 10 questions** → From shuffled pool
4. **Return to player**

### The Issue:
- If pool has exactly 10 questions → same questions, just different order
- If pool has 50+ questions → different subset each time!

### The Fix:
- **Populate 30-50 questions per category**
- With 50 questions, you can play 5 unique runs
- With 100 questions, you can play 10 unique runs

---

## 📊 Recommended Question Counts

| Dungeon Type | Minimum | Recommended | Ideal |
|--------------|---------|-------------|-------|
| Main Dungeons | 30 | 50 | 100 |
| New Dungeons | 20 | 30 | 50 |

**Why?**
- 30 questions = 3 unique runs
- 50 questions = 5 unique runs
- 100 questions = 10 unique runs
- More questions = more replayability!

---

## ⏱️ Population Time Estimate

OpenTDB limits: 1 request per 5 seconds

**Per Category (30 questions):**
- Easy: 1-2 requests (~10 seconds)
- Medium: 1-2 requests (~10 seconds)
- Hard: 1-2 requests (~10 seconds)
- **Total: ~30-60 seconds per category**

**All 4 New Categories (30 each):**
- **Total time: ~2-4 minutes**

**All 4 New Categories (50 each):**
- **Total time: ~5-10 minutes**

---

## 🎯 Check Progress

While it's populating, check progress:

```bash
docker-compose exec api poetry run python scripts/check_questions.py
```

You'll see question counts increase!

---

## ✅ After Population Complete

### Geography Dungeon Will Have:
- 50+ questions (instead of 10)
- Different questions each run
- Much better variety!

### All Dungeons Will Have:
- Enough questions for variety
- Multiple runs without repeats
- Better player experience

---

## 🎮 Test After Population

1. **Wait for population to complete** (~5-10 minutes)
2. **Check question counts** (should show 50+ for geography)
3. **Play geography dungeon** - Note the questions
4. **Play again** - Should see different questions!
5. **Play third time** - Even more different!

---

## 📝 Quick Reference

### Check Status:
```bash
docker-compose exec api poetry run python scripts/check_questions.py
```

### Populate Specific Category:
```bash
docker-compose exec api poetry run python scripts/populate_questions.py --category geography --count 50
```

### Populate All Categories:
```bash
docker-compose exec api poetry run python scripts/populate_questions.py --count 30
```

---

## 🎉 Summary

**Issue**: Geography has only 10 questions → same questions every run  
**Fix**: Populating 50+ questions → variety across multiple runs  
**Status**: 🔄 Running in background  
**Time**: ~5-10 minutes  
**Result**: Much better replayability!  

---

**The geography question population is running now! It will finish in ~5-10 minutes, then you'll have variety!** 🌍✨

