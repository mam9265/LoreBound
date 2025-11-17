# 🔍 Debugging Run Submission

## Current Issue

Getting "Submit run failed: Error: [object Object]" when completing dungeons.

## What I Just Added

### Enhanced Logging:

The frontend now logs detailed information when submitting:

```javascript
[RunService] Submitting run: {
  runId: "...",
  turnCount: 10,
  scoresCount: 10,
  sampleTurn: { question_index: 0, answer_index: 2, time_taken: 1.5 },
  sampleScore: { points: 100, answer_time: 1.5, is_correct: true, ... },
  isVictory: true,
  isDailyChallenge: false
}
```

### Pre-submission Validation:

- Checks turn count matches score count
- Validates all required score fields exist
- Shows clear error messages if data is malformed

---

## 🎮 Next Steps

### Try Playing Again:

1. **Open React Native console/debugger**
2. **Start a new dungeon run**
3. **Complete it (answer all questions)**
4. **Watch the console output**

You should now see:
- What data is being sent
- Any validation errors
- The actual API response

### What to Look For:

**If you see:**
```
[RunService] Data mismatch: 8 turns but 10 scores
```
→ There's a mismatch in data arrays

**If you see:**
```
[RunService] Invalid score at index 3
```
→ A score object is missing required fields

**If you see:**
```
[RunService] Submit failed: { status: 422, detail: [...] }
```
→ The actual backend validation error will be shown

---

## 🔧 Common Issues & Fixes

### Issue: Turn/Score count mismatch
**Cause:** Data arrays not same length  
**Fix:** Ensure every answer creates both a turn and score entry

### Issue: Missing score fields
**Cause:** Score missing required fields (points, answer_time, is_correct)  
**Fix:** Ensure all fields are populated in RunGameplay

### Issue: Invalid data types
**Cause:** Sending wrong data types (string instead of number, etc.)  
**Fix:** Transform data properly before sending

---

## 📊 Expected Data Format

### Turn Data:
```javascript
{
  question_index: 0,     // number
  answer_index: 2,       // number (0-3)
  time_taken: 1.82       // number (seconds)
}
```

### Score Data:
```javascript
{
  points: 130,           // number (>= 0)
  answer_time: 1.82,     // number (>= 0)
  is_correct: true,      // boolean
  streak_bonus: 10,      // number (>= 0)
  time_bonus: 5,         // number (>= 0)
  item_bonus: 15         // number (>= 0)
}
```

---

## 🚀 After You Try Again

**Share the console output** and I can immediately identify the issue!

The enhanced logging will show exactly what's wrong, making it easy to fix.

