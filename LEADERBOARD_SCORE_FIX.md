# Leaderboard Score Record Fix

## 🐛 Issue

**Problem:** Leaderboard shows 0 players even after completing runs

**Root Cause:** Score records were not being created in the `scores` table

## 🔍 What Was Happening

### Database State:
```sql
-- Runs table: ✅ Has completed run with score
SELECT * FROM runs WHERE status='completed';
-- Result: 1 run with total_score = 833

-- Scores table: ❌ Empty!
SELECT * FROM scores;
-- Result: 0 rows
```

### Leaderboard Logic:
- Leaderboard queries the `scores` table
- Scores table was empty
- Therefore: 0 players shown

### Why Scores Were Missing:
The `complete_run()` method only updated the Run record, but didn't create a Score record for the leaderboard system.

## ✅ Fix Applied

**File:** `lorebound-backend/app/services/run_service.py`

### Added Score Record Creation:

```python
# Create Score record for leaderboard
from ..domain.models import Score
score_record = Score(
    run_id=run_id,
    user_id=user_id,
    floor=run.floor,
    correct_count=correct_count,
    total_time_ms=total_time_ms,
    streak_max=streak_max,
    score=total_score
)
session.add(score_record)
await session.flush()
```

### What Gets Created:
- `run_id` - Links to the completed run
- `user_id` - Player who completed the run
- `floor` - Which floor was played
- `correct_count` - Number of correct answers
- `total_time_ms` - Total time taken
- `streak_max` - Best streak achieved
- `score` - Total score (used for rankings)
- `created_at` - Timestamp (auto-generated)

## 🎯 How Leaderboards Work Now

### When You Complete a Run:
```
1. Answer all questions ✅
2. Submit run ✅
3. Backend validates answers ✅
4. Backend calculates score ✅
5. Backend updates Run record ✅
6. Backend creates Score record ✅ (NEW!)
7. Score appears in leaderboard queries ✅
```

### Leaderboard Query:
```sql
-- All-time leaderboard
SELECT user_id, SUM(score) as total_score
FROM scores
GROUP BY user_id
ORDER BY total_score DESC;
```

### Scopes:
- **All-Time:** Sum of ALL your scores
- **Weekly:** Sum of scores from this week
- **Today:** Sum of scores from today

## 🎮 Test Again

**The backend has auto-reloaded.** Now:

### Option 1: Complete a New Run
1. Start a fresh dungeon run
2. Complete all 10 questions
3. Submit
4. View Leaderboard
5. **You should see yourself ranked!** ✅

### Option 2: Pull to Refresh
1. Go to Leaderboard screen
2. Pull down to refresh
3. **Still might show 0** because your old run didn't create a Score

**Recommendation:** Complete a new run to test properly!

## 🔍 Verify Your Old Run

Your previous run (833 points) didn't create a Score record, so it won't appear on leaderboards.

**To check:**
```powershell
docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM scores;"
# Should be 0 for now

# After you complete a NEW run:
# Should be 1 (or more)
```

## ✅ Expected After New Run

**Leaderboard All-Time:**
```
Rank  | Handle              | Score
------|---------------------|-------
  1   | IntegrationTester   | 850
```

**Leaderboard Today:**
```
Rank  | Handle              | Score
------|---------------------|-------
  1   | IntegrationTester   | 850
```

**Leaderboard Weekly:**
```
Rank  | Handle              | Score
------|---------------------|-------
  1   | IntegrationTester   | 850
```

## 📊 Multiple Runs

After completing multiple runs:

**Example - 3 Runs Completed:**
```
Run 1: 850 points (History)
Run 2: 720 points (Sports)
Run 3: 900 points (Music)

All-Time Leaderboard:
Your Total Score: 850 + 720 + 900 = 2470
Your Rank: #1 (if you're the only player)
```

## 🎯 What to Do Now

1. **Complete a NEW dungeon run**
   - Pick any dungeon
   - Answer all 10 questions
   - Submit successfully

2. **Check Leaderboard**
   - Should now show 1 participant (you!)
   - Your rank should be #1
   - Your score should be visible

3. **Try Multiple Runs**
   - Complete 2-3 more runs
   - Watch your total score increase
   - See leaderboard update

## 🐛 If Still Shows 0 Players

**Check if Score was created:**
```powershell
docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT * FROM scores;"
```

**Check backend logs:**
```powershell
docker logs lorebound-backend-api-1 --tail 20
# Look for: "Created score record for run..."
```

**Force cache refresh:**
- Pull down on leaderboard (pull-to-refresh)
- Or wait 30 seconds (cache expires)

---

## 🎉 Summary

**Fixed:** Score records now created when runs complete

**Result:** Leaderboard will show players who complete runs!

**Test:** Complete a new run and check leaderboard - you should appear! 🏆

---

**Go complete another run and become #1 on the leaderboard!** 🎮🏆

