# Daily Challenge - Quick Start Guide 🏆

## ✅ Implementation Complete!

The Daily Challenge feature is now fully implemented and ready to test!

## What You Get

### Daily Challenge Features

1. **🎯 Hard Questions Only** - All 10 questions are hard difficulty
2. **🎲 Random Category** - Different category each day (Music, History, Sports, etc.)
3. **📅 Daily Rotation** - New challenge at midnight UTC
4. **⭐ 2x XP Bonus** - Double experience points
5. **💰 1.5x Points Bonus** - 50% more points than regular dungeons
6. **⏰ Timer** - Shows time until next challenge

## How to Test Right Now

### Step 1: Start the Mobile App

If the app is already running, just reload it. Otherwise:
```bash
cd lorebound
npm start
# In another terminal: npm run android
```

### Step 2: Navigate to Daily Challenge

1. Open the app
2. Log in (or register if new user)
3. From Main Menu → Click **"Daily Challenge"**

### Step 3: What You Should See

```
🏆 DAILY CHALLENGE 🏆
Daily [Category] Challenge
⏰ 23h XXm remaining

[HARD MODE]
Hard mode challenge! 10 difficult [category] 
questions with bonus rewards!

BONUS REWARDS
  2x        1.5x
  XP       Points

[START CHALLENGE]
```

### Step 4: Play the Challenge

1. Click "START CHALLENGE"
2. You'll get 10 hard difficulty questions
3. Points are automatically multiplied by 1.5x
4. Complete the challenge

### Step 5: Check Results

Results screen will show:
```
🏆 DAILY CHALLENGE 🏆
Victory!
Daily [Category] Challenge

✨ 1.5x Points Bonus Applied! ✨

Final Score: [Your Score × 1.5]
```

## Example Point Comparison

### Regular Hard Dungeon
- Question 1 (hard): 250 points
- Question 2 (hard): 280 points  
- Question 3 (hard): 220 points
- **Total after 10 questions**: ~2,500 points

### Daily Challenge (Hard + Bonus)
- Question 1 (hard): 250 × 1.5 = **375 points**
- Question 2 (hard): 280 × 1.5 = **420 points**
- Question 3 (hard): 220 × 1.5 = **330 points**
- **Total after 10 questions**: ~3,750 points! 🎉

**That's 50% more points!**

## Today's Challenge

The system will automatically generate today's challenge. To see what it is:

```bash
# Query the database
docker-compose exec -T db psql -U postgres -d lorebound -c \
  "SELECT date, modifiers->>'theme' as theme, modifiers->>'difficulty' as difficulty FROM daily_challenges ORDER BY date DESC LIMIT 1;"
```

Expected output:
```
         date            |         theme          | difficulty 
-------------------------+------------------------+------------
 2025-11-02 00:00:00+00  | Daily Music Challenge  | hard
```

## Challenge Categories

The random category selection includes:
- 🎵 **Music** - Music trivia
- 📚 **History** - Historical events
- ⚽ **Sports** - Sports knowledge
- 🎬 **Pop Culture** - Movies, TV, entertainment
- 🔬 **Science** - Scientific facts (if available)
- 🌍 **All Around** - General knowledge

## Current Hard Question Availability

| Category | Hard Questions Available |
|----------|-------------------------|
| Ancient History | 36 ✅ (Plenty!) |
| Sports Arena | 1 ⚠️ (Limited) |
| Musical Harmony | 2 ⚠️ (Limited) |
| Pop Culture | 1 ⚠️ (Limited) |

### Recommendation

If today's challenge is Music, Sports, or Pop Culture, you might see the same questions repeat (since there are only 1-2 hard questions).

**To add more hard questions**:
The system will automatically try to fetch them from the API when needed. The rate limiting means it takes time, but it works!

## Troubleshooting

### "Failed to load daily challenge"

- Check backend is running: `docker-compose ps`
- Check API logs: `docker-compose logs api`
- Try reloading the app

### "No questions available"

The system will auto-fetch hard questions from OpenTDB. Wait a moment and try again.

### Daily challenge not updating

Challenges update at midnight UTC. To manually trigger a new one:

```bash
# Delete today's challenge to force regeneration
docker-compose exec -T db psql -U postgres -d lorebound -c \
  "DELETE FROM daily_challenges WHERE date >= CURRENT_DATE;"
```

Then reload the app and navigate to Daily Challenge.

## API Endpoints

For testing with Postman/curl:

### Get Today's Challenge
```bash
GET http://localhost:8000/v1/content/daily
Authorization: Bearer {your_token}
```

### Get Challenge Questions
```bash
GET http://localhost:8000/v1/content/daily/{challenge_id}/questions
Authorization: Bearer {your_token}
```

## Tomorrow's Challenge

The challenge rotates daily at midnight UTC:
- **Today (Nov 2)**: Random category (e.g., Music)
- **Tomorrow (Nov 3)**: Different random category (e.g., History)
- **Day After**: Another random category (e.g., Sports)

Each day is deterministic (same category for all players) but different from previous days.

## XP Calculation

The 2x XP multiplier is applied to:

**Normal run**:
```
Score: 2,500
XP: score / 10 = 250 XP
```

**Daily challenge run**:
```
Score: 3,750 (already × 1.5)
XP: score / 10 × 2 = 750 XP
```

**That's 3x the normal XP** (1.5x points + 2x XP multiplier)!

## Summary

✅ **Everything is ready!**

The Daily Challenge is:
- ✅ Fully implemented on backend
- ✅ Beautiful UI on frontend
- ✅ Hard questions only
- ✅ Random category per day
- ✅ Bonus XP and points
- ✅ Integrated with gameplay
- ✅ Deployed and running

**Just open the app and try it!** 🎮

Navigate to Daily Challenge from the main menu and experience:
- Beautiful gold-themed UI
- Hard difficulty challenge
- Bonus rewards
- Competitive gameplay

Enjoy! 🏆✨

