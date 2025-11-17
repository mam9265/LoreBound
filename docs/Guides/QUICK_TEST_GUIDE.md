# 🎮 Quick Test Guide - Your New Features!

**Status:** ✅ Code Updated, Backend Running, Ready to Test!

---

## 🚀 Test Everything (10 Minutes)

### ✅ Backend Status:
- Docker containers running
- API operational on http://localhost:8000
- Database connected
- 842 questions loaded
- 8 dungeons available

### ✅ Frontend Status:
- Latest code from GitHub
- CharacterCustomization updated
- All fixes applied

---

## 🎯 Test 1: Category Matching (2 min)

**What to test:** Questions match dungeon categories

1. **Start your frontend:**
   ```bash
   cd lorebound
   npm run android  # or npm run ios
   ```

2. **Login** to the game

3. **Go to Dungeon Select** - You should see 8 dungeons:
   - 🏛️ Ancient History Depths
   - ⚽ Sports Arena Challenge
   - 🎵 Musical Harmony Tower
   - 📺 Pop Culture Arcade
   - 📚 Library of Knowledge (NEW!)
   - 🔬 Science Laboratory (NEW!)
   - 🌍 Geography Explorer (NEW!)
   - 🌟 General Knowledge Arena (NEW!)

4. **Play Music dungeon**
   - ✅ All questions should be about music
   - ✅ NO coding, Pokemon, or random questions!

5. **Play Sports dungeon**
   - ✅ All questions should be about sports

**Expected:** Perfect category matching! 🎯

---

## ⚔️ Test 2: Item Effects (3 min)

**What to test:** Items provide gameplay bonuses

1. **Go to Character Customization**

2. **Look for these NEW items** (I added them to your account):
   - 🗡️ Legendary Sword of Power
   - 🪖 Epic Helmet of Wisdom
   - 🛡️ Epic Armor of Fortitude
   - 👢 Rare Boots of Speed
   - 🛡️ Rare Shield of Protection
   - 💍 Uncommon Ring of Knowledge

3. **Equip them** in each slot

4. **Start any dungeon**

5. **Look for green bonus banner** below stats:
   ```
   ⚔️ +92%    ⏱️ +13s    ✨ +35% XP
   ```

6. **Check timer** - Should start at **43 seconds** (not 30!)

7. **Answer questions** - Scores should be MUCH higher

8. **Complete the run** - Total score should be ~1,900+ (vs ~1,000 without items)

**Expected:** Visible bonuses that make gameplay easier and more rewarding! ⚔️

---

## 🎲 Test 3: Question Variety (2 min)

**What to test:** Different questions each run

1. **Play Geography dungeon** - Note the questions

2. **Play Geography again** - Note the questions

3. **Verify:** Different questions!

**Expected:** With 130 geography questions, each run shows different ones! 🎲

---

## 🎁 Test 4: Item Rewards (3 min)

**What to test:** Items drop after completing runs

1. **Complete a dungeon run** successfully (don't lose all lives)

2. **Victory screen** should show:
   ```
   🎁 Items Obtained! 🎁
   You earned X new items!
   
   [Item cards with rarity colors]
   ```

3. **Go to Character Customization**

4. **Verify:** New items appear in your inventory

**Expected:** Automatic item rewards! 🎁

---

## 🏆 Test 5: Daily Challenge (2 min)

**What to test:** Daily challenges work

1. **Main Menu** → **Daily Challenge**

2. **Click START CHALLENGE**

3. **Complete it**

4. **Victory screen** should show:
   - 2-3 items (better rewards!)
   - Higher rarity items
   - Bonus XP and points applied

**Expected:** Daily challenges give better loot! 🏆

---

## 📊 Quick Verification

### Check Backend Logs:

```bash
cd lorebound-backend
docker-compose logs api -f | Select-String -Pattern "equipped items|Rewarded"
```

When you start a run, you should see:
```
User has X equipped items with bonuses: {score_multiplier: 1.52, ...}
```

When you complete a run, you should see:
```
Rewarded Battle Axe (rare) to user ...
Distributed 2 rewards to user ...
```

### Check Question Counts:

```bash
docker-compose exec api poetry run python scripts/check_questions.py
```

Should show:
```
✓ All 8 dungeons with 80-130 questions each
Total: 842 questions
```

---

## 🎯 What You Should Experience

### Starting a Run:
1. Select dungeon → Loads instantly
2. Item bonuses calculated → Shown in green banner
3. Questions appear → All match category!
4. Timer extends → 30s + item bonuses

### During Gameplay:
1. See stats: Lives, Streak, Score, Timer
2. See bonuses: ⚔️ Score%, ⏱️ Time, ✨ XP%
3. Extended timer if items equipped
4. Higher scores from multipliers
5. Only category-matched questions

### Completing a Run:
1. Submit results → No errors!
2. Victory screen → Shows items earned
3. XP gained → Check profile
4. Run history → Shows dungeon name

---

## 🐛 If Something Doesn't Work:

### No item bonuses showing?
- Check items are **equipped** (not just owned)
- Look for items with `time_extension` and `xp_bonus` stats
- Old items only have `score_multiplier`

### Same questions every run?
- Check that category has 30+ questions
- Run: `docker-compose exec api poetry run python scripts/check_questions.py`

### Validation errors?
- Check React Native console for detailed error
- Backend logs show exact validation issue

### "Unknown Dungeon"?
- This is fixed in this update
- Restart app if you still see it

---

## ✅ Success Checklist

After testing, you should verify:

- [ ] Music dungeon shows only music questions ✅
- [ ] Green bonus banner displays (if items equipped) ✅
- [ ] Timer extends with items (30s → 40s+) ✅
- [ ] Scores are higher with items ✅
- [ ] Items drop after victories (1-3 based on score) ✅
- [ ] Run history shows "Musical Harmony Tower" etc. ✅
- [ ] Daily challenges work ✅
- [ ] Geography shows different questions each run ✅

---

## 🎉 Ready to Test!

**Everything is set up and ready:**

✅ Code updated from GitHub  
✅ Backend restarted and running  
✅ Database has 842 questions  
✅ 8 dungeons available  
✅ Test items in your inventory  

**Just start the app and play!** 🎮

---

## 🔗 Quick Commands

### Start Frontend:
```bash
cd lorebound
npm run android  # or npm run ios
```

### Check Logs:
```bash
cd lorebound-backend
docker-compose logs api -f
```

### Check Questions:
```bash
docker-compose exec api poetry run python scripts/check_questions.py
```

---

**Have fun testing all the new features!** 🎉✨

