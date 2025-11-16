# Dungeon Category Question Matching Fix

## Problem Summary

Questions were not matching dungeon categories correctly, causing random unrelated questions to appear when playing dungeons. For example, history questions might appear in a sports dungeon.

## Root Causes Identified

### 1. **Missing Category Mapping to OpenTDB**
The main issue was that LoreBound's dungeon categories (like `"sports"`, `"music"`, `"history"`, `"pop_culture"`) were not properly mapped to OpenTDB's category names:
- LoreBound: `"sports"` → OpenTDB: `"Sports"`
- LoreBound: `"music"` → OpenTDB: `"Entertainment: Music"`
- LoreBound: `"history"` → OpenTDB: `"History"`
- LoreBound: `"pop_culture"` → OpenTDB: Multiple entertainment categories

### 2. **Missing Dungeon Categories**
Several dungeon categories were missing from the backend enums but had frontend screens created:
- Books
- Science
- Geography
- General Knowledge

## Fixes Applied

### 1. **Updated Trivia API Client** (`lorebound-backend/app/services/trivia_api_client.py`)

Added a comprehensive category mapping system in the `_get_opentdb_category_id()` function:

```python
category_mapping = {
    "sports": "Sports",
    "music": "Entertainment: Music",
    "history": "History",
    "pop_culture": ["Entertainment: Television", "Entertainment: Film", 
                     "Entertainment: Video Games", "Entertainment: Board Games", 
                     "Entertainment: Comics"],
    "general": "General Knowledge",
    "science": "Science & Nature",
    "geography": "Geography",
    "books": "Entertainment: Books"
}
```

**Features:**
- Exact category name mapping
- Support for multiple OpenTDB categories (for `pop_culture`)
- Fallback to partial matching if exact match fails
- Detailed logging for debugging

### 2. **Added Missing Categories** (`lorebound-backend/app/domain/enums.py`)

Extended `DungeonCategory` enum with:
```python
class DungeonCategory(str, Enum):
    SPORTS = "sports"
    MUSIC = "music"
    HISTORY = "history"
    POP_CULTURE = "pop_culture"
    BOOKS = "books"          # NEW
    SCIENCE = "science"       # NEW
    GEOGRAPHY = "geography"   # NEW
    GENERAL = "general"       # NEW
```

### 3. **Updated Frontend Display** (`lorebound/src/services/ContentService.js`)

Added display names and icons for new categories:
- Books: 📚 "Books"
- Science: 🔬 "Science"
- Geography: 🌍 "Geography"
- General: 🌟 "General Knowledge"

### 4. **Expanded Seed Data** (`lorebound-backend/scripts/seed_content_data.py`)

Added four new dungeons:
- **Library of Knowledge** (Books)
- **Science Laboratory** (Science)
- **Geography Explorer** (Geography)
- **General Knowledge Arena** (General)

## How It Works Now

### Question Selection Flow

1. **User selects a dungeon** (e.g., "Sports Arena Challenge")
2. **Backend identifies dungeon category** (`sports`)
3. **Questions are fetched** from database filtered by dungeon category
4. **If insufficient questions**, the system:
   - Maps `"sports"` to OpenTDB's `"Sports"` category
   - Fetches questions from OpenTDB API
   - Stores them in the database linked to the Sports dungeon
   - Returns questions for gameplay

### Category Mapping Examples

| LoreBound Category | OpenTDB Category |
|-------------------|-----------------|
| `sports` | `Sports` |
| `music` | `Entertainment: Music` |
| `history` | `History` |
| `pop_culture` | `Entertainment: Television`, `Entertainment: Film`, etc. |
| `books` | `Entertainment: Books` |
| `science` | `Science & Nature` |
| `geography` | `Geography` |
| `general` | `General Knowledge` |

## How to Populate Questions

### Option 1: Automatic Population (Recommended)

Run the question population script for all categories:

```bash
cd lorebound-backend
python scripts/populate_questions.py
```

This will fetch 100 questions per category across all difficulty levels.

### Option 2: Populate Specific Category

For a specific category:

```bash
python scripts/populate_questions.py --category sports --count 100
```

Available categories:
- `sports`
- `music`
- `history`
- `pop_culture`
- `books`
- `science`
- `geography`
- `general`

### Option 3: Populate Specific Difficulty

For specific difficulty level:

```bash
python scripts/populate_questions.py --difficulty hard --count 50
```

### Option 4: Targeted Population

For category + difficulty combination:

```bash
python scripts/populate_questions.py --category history --difficulty easy --count 50
```

## Verifying the Fix

### 1. Check Backend Logs

When questions are fetched, you should see logs like:
```
INFO: Mapped 'sports' to OpenTDB category: 'Sports' (ID: 21)
INFO: Selected 10 questions from pool of 150 (category: sports, seed: 12345)
```

### 2. Test Each Dungeon

1. Start the backend:
   ```bash
   cd lorebound-backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd lorebound
   npm run android  # or npm run ios
   ```

3. Play each dungeon and verify questions match the category:
   - **Sports Arena** → Should only have sports questions
   - **Musical Harmony Tower** → Should only have music questions
   - **Ancient History Depths** → Should only have history questions
   - **Pop Culture Arcade** → Should have TV, film, gaming questions
   - **Library of Knowledge** → Should have book/literature questions
   - **Science Laboratory** → Should have science questions
   - **Geography Explorer** → Should have geography questions
   - **General Knowledge Arena** → Should have mixed general trivia

### 3. Check Database

Verify questions are properly categorized:

```bash
cd lorebound-backend
python -c "
from app.repositories.base import get_session
from app.domain.models import Question, Dungeon
from sqlalchemy import select
import asyncio

async def check():
    async for session in get_session():
        result = await session.execute(select(Dungeon))
        dungeons = result.scalars().all()
        
        for dungeon in dungeons:
            q_result = await session.execute(
                select(Question).where(Question.dungeon_id == dungeon.id)
            )
            count = len(list(q_result.scalars().all()))
            print(f'{dungeon.title} ({dungeon.category}): {count} questions')
        break

asyncio.run(check())
"
```

## Resetting Questions (If Needed)

If you have incorrectly categorized questions in your database, you can reset them:

### WARNING: This will delete all questions!

```sql
-- Connect to PostgreSQL database
psql -U postgres -d lorebound

-- Delete all questions
DELETE FROM questions;

-- Verify
SELECT COUNT(*) FROM questions;  -- Should be 0
```

Then repopulate:
```bash
cd lorebound-backend
python scripts/populate_questions.py
```

## Future Enhancements

### Adding New Categories

To add a new dungeon category:

1. **Add to backend enum** (`app/domain/enums.py`):
   ```python
   class DungeonCategory(str, Enum):
       # ... existing categories ...
       MY_NEW_CATEGORY = "my_new_category"
   ```

2. **Add mapping in trivia client** (`app/services/trivia_api_client.py`):
   ```python
   category_mapping = {
       # ... existing mappings ...
       "my_new_category": "OpenTDB Category Name"
   }
   ```

3. **Add to frontend** (`lorebound/src/services/ContentService.js`):
   ```javascript
   const displayNames = {
       // ... existing names ...
       'my_new_category': 'My Category Name',
   };
   
   const icons = {
       // ... existing icons ...
       'my_new_category': '🎯',
   };
   ```

4. **Create dungeon in seed data** (`scripts/seed_content_data.py`):
   ```python
   {
       "title": "My New Dungeon",
       "category": DungeonCategory.MY_NEW_CATEGORY,
       "modifiers": {...},
       "tiers": [...]
   }
   ```

5. **Populate questions**:
   ```bash
   python scripts/populate_questions.py --category my_new_category
   ```

## OpenTDB Category Reference

For reference, OpenTDB has these categories:

| ID | Category Name |
|----|--------------|
| 9 | General Knowledge |
| 10 | Entertainment: Books |
| 11 | Entertainment: Film |
| 12 | Entertainment: Music |
| 13 | Entertainment: Musicals & Theatres |
| 14 | Entertainment: Television |
| 15 | Entertainment: Video Games |
| 16 | Entertainment: Board Games |
| 17 | Science & Nature |
| 18 | Science: Computers |
| 19 | Science: Mathematics |
| 20 | Mythology |
| 21 | Sports |
| 22 | Geography |
| 23 | History |
| 24 | Politics |
| 25 | Art |
| 26 | Celebrities |
| 27 | Animals |
| 28 | Vehicles |
| 29 | Entertainment: Comics |
| 30 | Science: Gadgets |
| 31 | Entertainment: Japanese Anime & Manga |
| 32 | Entertainment: Cartoon & Animations |

## Support

If questions still don't match categories:

1. **Check backend logs** for category mapping
2. **Verify dungeon category** in database matches enum value
3. **Ensure questions exist** for that category
4. **Run populate_questions.py** to fetch more questions
5. **Check OpenTDB API** status at https://opentdb.com/

## Summary

The fix ensures that:
✅ Questions always match their dungeon's category
✅ OpenTDB API categories are properly mapped
✅ All dungeon types are supported (8 total)
✅ New categories can be easily added
✅ Frontend properly displays all categories
✅ Question population is automated and reliable

The root cause was a missing mapping layer between LoreBound's category names and OpenTDB's category names. This is now fixed with a robust mapping system.

