# Questions API Format Fix

## 🐛 Issue

**Error:** "No questions available for this dungeon"

**Root Cause:** API response format mismatch

## 🔍 What Was Wrong

### **API Response Format:**
```json
{
  "questions": [
    {
      "id": "...",
      "prompt": "Question text?",
      "choices": ["A", "B", "C", "D"],
      "difficulty": "easy",
      "tags": [...]
      // NOTE: No answer_index!
    }
  ],
  "seed": 4031005187,
  "dungeon_id": "...",
  "floor": 1
}
```

### **Frontend Expected:**
```javascript
// Expected array directly:
[
  { id, prompt, choices, answer_index, ... }
]
```

## ✅ Fixes Applied

### 1. **RunService.js - Extract Questions Array**

Changed:
```javascript
return data;  // Returns whole object
```

To:
```javascript
return data.questions || [];  // Returns just the questions array
```

### 2. **RunGameplay.js - Remove Client-Side Answer Validation**

**Security Feature:** The backend doesn't send `answer_index` to prevent cheating!

**Before:**
- Frontend knew correct answers
- Showed green/red immediately
- Client-side validation

**After:**
- Frontend doesn't know correct answers
- Just records what user selected
- Backend validates when run is submitted
- Results shown at the end

### 3. **Updated UI Behavior**

**Changed:**
- ❌ No more green/red answer highlighting during gameplay
- ✅ Just shows selected answer (blue highlight)
- ✅ Score/lives update optimistically
- ✅ Real validation happens on backend
- ✅ Actual results shown in RunResults screen

## 🎮 How It Works Now

### **During Gameplay:**
1. User selects an answer → Highlights blue
2. User clicks "Submit Answer"
3. Question advances to next
4. Score shown is optimistic (assumes correct)
5. Lives don't decrease (can't validate yet)

### **After Completing Run:**
1. All answers submitted to backend
2. Backend validates each answer
3. Backend calculates real score
4. RunResults screen shows actual results
5. Leaderboard updates with real score

## 📊 Flow Diagram

```
User Answers Questions (Frontend)
    ↓
Records answers (no validation)
    ↓
Submits all answers to backend
    ↓
Backend validates each answer ✅
    ↓
Backend calculates score ✅
    ↓
Backend saves run ✅
    ↓
Returns results to frontend ✅
    ↓
Shows RunResults screen ✅
```

## 🔐 Security Benefits

**Why backend doesn't send answer_index:**
- ✅ Prevents cheating via JavaScript inspection
- ✅ Prevents automated bots from knowing answers
- ✅ Ensures score integrity
- ✅ Server-side validation is trustworthy

## 🎯 What You'll See Now

### **Loading Questions:**
```
Loading Dungeon...
```

### **Gameplay Screen:**
```
Question 1/10
Score: 0 (optimistic)
Lives: ❤️❤️❤️
Timer: 30s

[Question text]

A) Choice 1
B) Choice 2 (← Selected, blue highlight)
C) Choice 3
D) Choice 4

[Submit Answer Button]
```

### **After Submit:**
- Moves to next question immediately
- No red/green feedback
- Score increases optimistically
- All validated at the end

### **Results Screen:**
```
Run Complete!
Final Score: 850
Questions Answered: 10
Correct: 8
Incorrect: 2
Accuracy: 80%
Max Streak: 5
```

## ✅ Try It Now!

The app should auto-reload. Then:

1. **Go to Dungeon Select**
2. **Tap any dungeon**
3. **You should see:**
   - "Loading Dungeon..." (2-3 seconds)
   - Then gameplay screen with questions!
4. **Answer questions:**
   - Tap an answer → Highlights blue
   - Tap "Submit Answer" → Next question
   - Continue for all 10 questions
5. **See real results** at the end!

## 🐛 If Still Issues

**Check Metro logs for:**
```
Initializing run for dungeon: [UUID]
Run started: {run data}
Questions received: 10
```

**If "Questions received: 0":**
- Backend doesn't have questions
- Run: `.\quick_test.ps1` to verify

**If still errors:**
- Share Metro terminal output
- Check backend logs: `docker logs lorebound-backend-api-1`

---

**Try tapping a dungeon now!** You should be able to play through all 10 questions! 🎮

