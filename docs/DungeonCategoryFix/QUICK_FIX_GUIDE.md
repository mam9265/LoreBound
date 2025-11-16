# Quick Fix Guide - Dungeon Category Questions

## What Was Fixed

✅ Questions now properly match dungeon categories  
✅ Added proper mapping between game categories and OpenTDB API  
✅ Added 4 new dungeon types (Books, Science, Geography, General)  
✅ Frontend now displays all category types correctly  

## Quick Test (5 minutes)

### Step 1: Update Backend
```bash
cd lorebound-backend

# Make sure backend has latest code
# (Your changes are already applied)
```

### Step 2: Reseed Dungeons (Optional - if you want new categories)
```bash
# Only run this if you want to add the new dungeon types
# WARNING: This will only work if you don't have dungeons yet
python scripts/seed_content_data.py
```

### Step 3: Populate Questions
```bash
# Populate questions for all categories
python scripts/populate_questions.py

# OR populate specific categories:
python scripts/populate_questions.py --category sports --count 50
python scripts/populate_questions.py --category music --count 50
python scripts/populate_questions.py --category history --count 50
python scripts/populate_questions.py --category pop_culture --count 50
```

### Step 4: Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Start Frontend
```bash
cd lorebound
npm run android
# or
npm run ios
```

### Step 6: Test
1. Login to the game
2. Go to Dungeon Select
3. Play each dungeon
4. **Verify**: Questions now match the dungeon category!
   - Sports dungeon → Only sports questions ⚽
   - Music dungeon → Only music questions 🎵
   - History dungeon → Only history questions 🏛️
   - Pop Culture → Only TV/Film/Gaming questions 📺

## What If I Still See Wrong Questions?

### Issue: Still getting random questions

**Solution 1**: Clear old questions and repopulate
```bash
cd lorebound-backend

# Connect to database and clear questions
python -c "
from app.repositories.base import get_session
from app.domain.models import Question
from sqlalchemy import delete
import asyncio

async def clear():
    async for session in get_session():
        await session.execute(delete(Question))
        await session.commit()
        print('Cleared all questions')
        break

asyncio.run(clear())
"

# Repopulate with correct categories
python scripts/populate_questions.py
```

**Solution 2**: Check backend logs
```bash
# Look for category mapping logs
# You should see:
# INFO: Mapped 'sports' to OpenTDB category: 'Sports' (ID: 21)
```

**Solution 3**: Verify dungeon categories
```bash
python -c "
from app.repositories.base import get_session
from app.domain.models import Dungeon
from sqlalchemy import select
import asyncio

async def check():
    async for session in get_session():
        result = await session.execute(select(Dungeon))
        for d in result.scalars().all():
            print(f'{d.title}: {d.category}')
        break

asyncio.run(check())
"
```

## Category Mappings

| Your Dungeon | OpenTDB Fetches From |
|-------------|---------------------|
| Sports Arena | Sports |
| Musical Harmony | Entertainment: Music |
| History Depths | History |
| Pop Culture | TV/Film/Gaming |
| Library (Books) | Entertainment: Books |
| Science Lab | Science & Nature |
| Geography | Geography |
| General Knowledge | General Knowledge |

## Files Changed

1. ✅ `lorebound-backend/app/services/trivia_api_client.py` - Added category mapping
2. ✅ `lorebound-backend/app/domain/enums.py` - Added new categories
3. ✅ `lorebound-backend/scripts/seed_content_data.py` - Added new dungeons
4. ✅ `lorebound/src/services/ContentService.js` - Added category displays

## Need Help?

See the detailed guide: `DUNGEON_CATEGORY_FIX.md`

## Summary

The fix is complete! The issue was that your game's category names (like "sports") weren't matching OpenTDB's category names (like "Sports" or "Entertainment: Music"). Now there's a proper mapping layer that ensures questions always match their dungeon's category.

Just repopulate your questions and you're good to go! 🎮

