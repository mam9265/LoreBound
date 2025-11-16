# 🎮 Test Item Effects - Quick Guide

## ✅ Status: READY TO TEST!

**What's done:**
- ✅ Backend loads equipped items and calculates bonuses
- ✅ Frontend applies bonuses to gameplay
- ✅ 7 test items added to your inventory
- ✅ Green bonus banner displays active effects
- ✅ Scores are higher with items equipped

---

## 🚀 Test It RIGHT NOW!

### Step 1: Equip Items (2 minutes)

1. Open your game
2. Go to **Character Customization**
3. **Equip these items** (they're in your inventory):
   - ⚔️ **Legendary Sword of Power** → 35% score bonus + 5s extra time!
   - 🪖 **Epic Helmet of Wisdom** → 15% score bonus + 20% XP
   - 🛡️ **Epic Armor of Fortitude** → 10% score bonus + 3s extra time
   - 👢 **Rare Boots of Speed** → 3s extra time + 10% XP
   - 🛡️ **Rare Shield of Protection** → 5% score bonus
   - 💍 **Uncommon Ring of Knowledge** → 2s extra time + 5% XP
   - 📿 **Uncommon Amulet of Focus** → 5 streak bonus

4. You should see items in slots:

### Step 2: Start a Dungeon Run

1. Go to **Dungeon Select**
2. Choose **Music Dungeon** (has properly categorized questions now!)
3. **Start the run**

### Step 3: Watch for Item Effects

**You should see:**

1. **Green Bonus Banner** under stats:
   ```
   ⚔️ +92%   ⏱️ +13s   ✨ +35% XP
   ```
   
   Breaking down the bonuses:
   - Score: 1.35 × 1.15 × 1.1 × 1.05 = 1.92x (92% bonus!)
   - Time: 5 + 3 + 3 + 2 = 13 extra seconds!
   - XP: 20% + 10% + 5% = 35% bonus!

2. **Timer starts at 43 seconds** instead of 30!
   - Base: 30s
   - Bonus: +13s
   - Total: **43 seconds** to answer each question

3. **Higher Scores** per question:
   - Without items: 100 points (easy question)
   - With items: **192 points** (1.92x multiplier!)

### Step 4: Compare

Try a run **with** vs **without** items:

| Metric | Without Items | With All Items |
|--------|--------------|----------------|
| Timer | 30s | 43s (+13s) |
| Easy Question | 100 pts | 192 pts |
| Medium Question | 150 pts | 288 pts |
| Hard Question | 200 pts | 384 pts |
| Total for 10Q | ~1,000 pts | ~1,920 pts |
| XP Gained | Base | +35% bonus |

---

## 🔍 What to Look For

### Backend Logs

```bash
docker-compose logs api -f
```

When you start a run, you should see:
```
INFO: User X has 7 equipped items with bonuses: {
  'score_multiplier': 1.9224..., 
  'time_extension': 13, 
  'xp_bonus': 0.35
}
```

### In-Game

1. **Stats Row** (at top):
   - Lives, Streak, Score, Timer

2. **Green Bonus Banner** (NEW!):
   - Shows active item bonuses
   - ⚔️ Score percentage
   - ⏱️ Time extension
   - ✨ XP percentage

3. **Extended Timer**:
   - Should start at 43 instead of 30
   - More time to think and answer!

4. **Higher Scores**:
   - Points per question nearly doubled
   - Total score much higher at end

---

## 💡 Testing Scenarios

### Test 1: Full Gear Set
- Equip all 7 items
- Run Music dungeon
- Expected: ~1,900 points for 10 questions

### Test 2: No Items
- Unequip everything
- Run same dungeon
- Expected: ~1,000 points for 10 questions

### Test 3: Partial Gear
- Equip only weapon + helmet
- Expected: 1.35 × 1.15 = 1.55x bonus (55%)
- Score: ~1,550 points for 10 questions

### Test 4: Time Extension
- Equip items with time_extension
- Verify timer shows 43s instead of 30s
- You have more time to think!

---

## 🎯 Item Bonuses Breakdown

### All 7 Test Items Combined:

**Score Multiplier:**
- Sword: 1.35x
- Helmet: 1.15x
- Armor: 1.1x
- Shield: 1.05x
- **Total: 1.92x** (92% bonus!)

**Time Extension:**
- Sword: +5s
- Armor: +3s
- Boots: +3s
- Ring: +2s
- **Total: +13 seconds**

**XP Bonus:**
- Helmet: +20%
- Boots: +10%
- Ring: +5%
- **Total: +35% more XP**

**Other:**
- Amulet: +5 streak bonus
- Sword: +15 streak bonus

---

## ✅ Expected Results

When you play with all items equipped:

| Aspect | Effect |
|--------|--------|
| **Timer** | 43 seconds (30 + 13) |
| **Score Per Q** | Nearly double! |
| **Total Score** | ~1,900 instead of ~1,000 |
| **XP After Run** | 35% more XP earned |
| **Visual** | Green bonus banner |
| **Feel** | More powerful, easier gameplay |

---

## 📊 Verification

### In Character Customization:
- You should see 7 new items in inventory
- Equip them in: Weapon, Helmet, Armor, Shield, Boots, Ring, Amulet

### In Dungeon Gameplay:
- Green banner appears below stats
- Timer shows 43s (not 30s)
- Scores are much higher
- Backend logs show bonuses

### In Run Results:
- Total score significantly higher
- More XP gained

---

## 🎉 Success Criteria

✅ Green bonus banner shows during gameplay  
✅ Timer extends to 43 seconds  
✅ Scores are ~2x higher with items  
✅ Backend logs show "User has X equipped items with bonuses"  
✅ Items make a meaningful difference  

---

## 🐛 Troubleshooting

### No bonus banner showing?
- Check items are **equipped** (not just owned)
- Restart the app
- Check backend logs

### Timer not extended?
- Verify items have `time_extension` stat
- Check console logs: `[RunGameplay] Time per question: 43 seconds`

### Scores not higher?
- Check console logs for item bonuses
- Verify `score_multiplier` > 1.0
- Try with vs without items to compare

---

## 🚀 GO TEST IT!

1. Open the game
2. Go to Character Customization
3. Equip the 7 new items
4. Start any dungeon
5. **Enjoy your powerful gear!** ⚔️🛡️✨

**Items now make you stronger in dungeons!**

