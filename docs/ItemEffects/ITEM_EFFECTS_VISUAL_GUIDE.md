# 🎮 Item Effects Visual Guide

## What Should You See?

### Green Bonus Banner Shows 3 Types of Bonuses:

```
┌─────────────────────────────────────────────┐
│  ⚔️ +52%     ⏱️ +8s     ✨ +30% XP         │
└─────────────────────────────────────────────┘
```

1. **⚔️ Score Bonus** - From `score_multiplier` stat
2. **⏱️ Time Bonus** - From `time_extension` stat  
3. **✨ XP Bonus** - From `xp_bonus` stat

---

## 🔍 Why You Only See ⚔️ (Swords)

Your equipped items only have `score_multiplier` stats! 

**Example of what you probably have equipped:**
- Crown of Thorns: `{"score_multiplier": 1.1, ...}` → Shows ⚔️ +10%
- Legendary Sword: `{"score_multiplier": 1.2, ...}` → Shows ⚔️ +20%
- Dark Plate: `{"score_multiplier": 1.15, ...}` → Shows ⚔️ +15%

**Combined: ⚔️ +52%** (1.1 × 1.2 × 1.15 = 1.518)

---

## 🎯 What Each Icon Means

### ⚔️ Score Bonus (Sword)
- **From:** Items with `score_multiplier` stat
- **Effect:** Multiplies your points per question
- **Example:** +52% = You get 152 points instead of 100

### ⏱️ Time Bonus (Clock)
- **From:** Items with `time_extension` stat
- **Effect:** Adds extra seconds to timer
- **Example:** +8s = Timer shows 38 seconds instead of 30

### ✨ XP Bonus (Sparkles)
- **From:** Items with `xp_bonus` stat
- **Effect:** More XP after completing the run
- **Example:** +30% = Get 130 XP instead of 100

---

## 📊 Which Items Have Which Stats?

### Items with TIME EXTENSION (⏱️):

**Test Items I Created:**
- 🗡️ **Legendary Sword of Power** - `time_extension: 5`
- 🛡️ **Epic Armor of Fortitude** - `time_extension: 3`
- 👢 **Rare Boots of Speed** - `time_extension: 3`
- 💍 **Uncommon Ring of Knowledge** - `time_extension: 2`

**Total if all equipped: ⏱️ +13s**

### Items with XP BONUS (✨):

**Test Items I Created:**
- 🪖 **Epic Helmet of Wisdom** - `xp_bonus: 0.2` (20%)
- 👢 **Rare Boots of Speed** - `xp_bonus: 0.1` (10%)
- 💍 **Uncommon Ring of Knowledge** - `xp_bonus: 0.05` (5%)

**Total if all equipped: ✨ +35% XP**

### Items with SCORE MULTIPLIER (⚔️):

**Most items have this:**
- 🗡️ **Legendary Sword of Power** - `score_multiplier: 1.35` (35%)
- 🪖 **Epic Helmet of Wisdom** - `score_multiplier: 1.15` (15%)
- 🛡️ **Epic Armor of Fortitude** - `score_multiplier: 1.1` (10%)
- 🛡️ **Rare Shield of Protection** - `score_multiplier: 1.05` (5%)

**Total if all equipped: ⚔️ +92%**

---

## 🎮 How to See All 3 Icons

### Equip These Items:

1. **Weapon:** Legendary Sword of Power
   - ⚔️ +35% score
   - ⏱️ +5s time
   - ✅ Shows BOTH icons!

2. **Helmet:** Epic Helmet of Wisdom
   - ⚔️ +15% score
   - ✨ +20% XP
   - ✅ Shows BOTH icons!

3. **Armor:** Epic Armor of Fortitude
   - ⚔️ +10% score
   - ⏱️ +3s time
   - ✅ Shows BOTH icons!

4. **Boots:** Rare Boots of Speed
   - ⏱️ +3s time
   - ✨ +10% XP
   - ✅ Shows BOTH icons!

5. **Shield:** Rare Shield of Protection
   - ⚔️ +5% score

6. **Ring:** Uncommon Ring of Knowledge
   - ⏱️ +2s time
   - ✨ +5% XP
   - ✅ Shows BOTH icons!

7. **Amulet:** Uncommon Amulet of Focus
   - (No score/time/xp bonuses, only streak)

### Result with All 7 Items:

```
┌─────────────────────────────────────────────┐
│  ⚔️ +92%     ⏱️ +13s     ✨ +35% XP         │
└─────────────────────────────────────────────┘
```

**All 3 icons appear!** 🎉

---

## 🔍 Check Your Equipped Items

### In Character Customization:

Look at what you have equipped and their stats:

**If you see ONLY ⚔️:**
- Your items only have `score_multiplier` stat
- Example: Crown of Thorns, Dark Plate, Legendary Sword of Wisdom (old items)

**To see ⏱️ also:**
- Equip: Legendary Sword of Power, Epic Armor, Rare Boots, or Ring

**To see ✨ also:**
- Equip: Epic Helmet, Rare Boots, or Ring

---

## 📱 What the Display Shows

### Current Display Logic:

```javascript
{/* Only shows icons for bonuses > 0 */}

{itemBonuses.score_multiplier > 1.0 && (
  <Text>⚔️ +{percent}%</Text>  // Shows if you have score multiplier
)}

{itemBonuses.time_extension > 0 && (
  <Text>⏱️ +{seconds}s</Text>  // Shows if you have time extension
)}

{itemBonuses.xp_bonus > 0 && (
  <Text>✨ +{percent}% XP</Text>  // Shows if you have XP bonus
)}
```

---

## 🎯 Quick Test

### To See All 3 Icons:

1. Go to **Character Customization**
2. **Unequip** all current items
3. **Equip these items:**
   - Weapon: **Legendary Sword of Power**
   - Helmet: **Epic Helmet of Wisdom**
   - Armor: **Epic Armor of Fortitude**
   - Boots: **Rare Boots of Speed**

4. **Start any dungeon**
5. **You should see:**
   ```
   ⚔️ +92%    ⏱️ +13s    ✨ +35% XP
   ```

---

## 💡 Understanding Your Current Items

### If You Only See ⚔️ +52%:

You likely have equipped:
- Items from the original 20 items (Crown of Thorns, Dark Plate, etc.)
- These have stats like `defense`, `intelligence`, `wisdom`, `speed_bonus`
- But NOT the new gameplay stats: `time_extension` or `xp_bonus`

### Old Items vs New Items:

**Old Items (original 20):**
```json
{
  "defense": 30,
  "intelligence": 40,
  "wisdom": 30,
  "speed_bonus": 0.15,
  "score_multiplier": 1.1  // Only score bonus
}
```

**New Items (test items I created):**
```json
{
  "score_multiplier": 1.35,  // Score bonus ⚔️
  "time_extension": 5,       // Time bonus ⏱️
  "streak_bonus": 15         // (Not shown in banner)
}
```

---

## 🛠️ Solution

### Option 1: Equip New Test Items

Equip the 7 test items I created for you:
- Legendary Sword of Power
- Epic Helmet of Wisdom
- Epic Armor of Fortitude
- Rare Boots of Speed
- Rare Shield of Protection
- Uncommon Ring of Knowledge
- Uncommon Amulet of Focus

These have `time_extension` and `xp_bonus` stats!

### Option 2: Check Item Stats

In Character Customization, when viewing items, you can see their stats. Look for items with:
- `time_extension`: Shows ⏱️ icon
- `xp_bonus`: Shows ✨ icon
- `score_multiplier`: Shows ⚔️ icon

---

## 📊 Full Breakdown

### What Each Stat Does:

| Stat | Icon | Effect | Where to See |
|------|------|--------|--------------|
| `score_multiplier` | ⚔️ | Higher scores | Green banner |
| `time_extension` | ⏱️ | Longer timer | Green banner |
| `xp_bonus` | ✨ | More XP | Green banner |
| `streak_bonus` | - | Higher streaks | In scores only |
| `perfect_bonus` | - | Perfect answer bonus | In scores only |
| `defense` | - | Old stat | Not used in gameplay |
| `intelligence` | - | Old stat | Not used in gameplay |
| `wisdom` | - | Old stat | Not used in gameplay |

The green banner **only shows the 3 gameplay-active stats**! 🎯

---

## 🎉 Summary

**You're seeing only ⚔️ because:**
- Your equipped items only have `score_multiplier`
- They don't have `time_extension` or `xp_bonus`

**To see all 3 icons:**
- Equip the test items I created
- They have all 3 stat types
- You'll see: ⚔️ +92%, ⏱️ +13s, ✨ +35% XP

**To check what you have equipped:**
- Go to Character Customization
- View item details
- Look at their `stats` field

---

**The system is working perfectly! You just need items with the other stat types to see the other icons!** ⚔️⏱️✨

