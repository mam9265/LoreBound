# Item Effects Implementation Guide

## Overview

Items now provide real gameplay benefits during dungeon runs! Equipped items give bonuses that help you score higher, answer faster, and progress better.

---

## ✨ Item Stat Types

### Score Bonuses
- **`score_multiplier`** (float): Multiplies your final score per question
  - Example: `1.15` = 15% more points
  - Multiple items multiply together (1.1 × 1.2 = 1.32x total)

- **`streak_bonus`** (int): Flat bonus points added to streak multipliers
  - Example: `5` = +5 points per streak level
  - Multiple items add together

### Time Bonuses
- **`time_extension`** (int): Extra seconds per question
  - Example: `3` = 3 more seconds to answer
  - Multiple items add together
  
- **`time_bonus_multiplier`** (float): Multiplies time bonus rewards
  - Example: `1.2` = 20% more points for fast answers

### XP & Progression
- **`xp_bonus`** (float): Extra XP multiplier after runs
  - Example: `0.2` = 20% more XP earned
  - Multiple items add together

- **`perfect_bonus`** (int): Bonus points for perfect (fast + correct) answers
  - Example: `10` = +10 points for perfect answers

---

## 🔧 How It Works

### 1. Starting a Run

When you start a dungeon run, the backend:

1. **Loads your equipped items** from all slots (weapon, armor, helmet, etc.)
2. **Calculates total bonuses**:
   - Multipliers (like `score_multiplier`) multiply together
   - Additive bonuses (like `time_extension`) add together
3. **Returns bonuses to frontend** in the run start response

**API Response Example:**
```json
{
  "run_id": "...",
  "seed": 123456,
  "session_token": "...",
  "equipped_items": [
    {
      "item_id": "...",
      "name": "Sword of Swift Answers",
      "slot": "weapon",
      "rarity": "epic",
      "stats": {
        "score_multiplier": 1.15,
        "time_extension": 3
      }
    },
    {
      "item_id": "...",
      "name": "Helmet of Wisdom",
      "slot": "helmet",
      "rarity": "rare",
      "stats": {
        "score_multiplier": 1.1,
        "xp_bonus": 0.15
      }
    }
  ],
  "total_bonuses": {
    "score_multiplier": 1.265,  // 1.15 × 1.1 = 1.265
    "time_extension": 3,
    "xp_bonus": 0.15
  }
}
```

### 2. During Gameplay

The frontend should:

1. **Store the bonuses** from the start response
2. **Apply time extensions** to question timers
3. **Calculate scores with multipliers**:
   ```javascript
   baseScore = 100;
   withStreak = baseScore + streakBonus;
   withTimeBonus = withStreak + timeBonus;
   withItemBonus = withTimeBonus * score_multiplier;
   finalScore = Math.floor(withItemBonus);
   ```
4. **Track item_bonus separately** for display and submission

### 3. Submitting Results

When submitting, include `item_bonus` in each score:

```json
{
  "turn_data": [...],
  "scores": [
    {
      "points": 130,          // Final score
      "answer_time": 2.5,
      "is_correct": true,
      "streak_bonus": 10,
      "time_bonus": 5,
      "item_bonus": 15        // Points from items
    }
  ],
  "client_signature": "..."
}
```

---

## 📊 Item Rarity Guidelines

### Recommended Stat Ranges by Rarity:

| Rarity | score_multiplier | time_extension | xp_bonus |
|--------|-----------------|----------------|----------|
| **Common** | 1.0 - 1.05 | 0 - 1 | 0 - 0.05 |
| **Uncommon** | 1.05 - 1.1 | 1 - 2 | 0.05 - 0.1 |
| **Rare** | 1.1 - 1.15 | 2 - 3 | 0.1 - 0.15 |
| **Epic** | 1.15 - 1.25 | 3 - 5 | 0.15 - 0.25 |
| **Legendary** | 1.25 - 1.5 | 5 - 10 | 0.25 - 0.5 |

---

## 🎮 Frontend Integration

### Step 1: Update RunGameplay to Store Bonuses

```javascript
const [itemBonuses, setItemBonuses] = useState({});
const [equippedItems, setEquippedItems] = useState([]);

// When starting run:
const response = await RunService.startRun(dungeonId);
setItemBonuses(response.total_bonuses);
setEquippedItems(response.equipped_items);
```

### Step 2: Apply Time Extension

```javascript
const baseTimePerQuestion = 30; // seconds
const actualTime = baseTimePerQuestion + (itemBonuses.time_extension || 0);

// Use actualTime for countdown timer
```

### Step 3: Calculate Score with Multiplier

```javascript
function calculateScore(basePoints, isCorrect, timeTaken, streak) {
  if (!isCorrect) return 0;
  
  let score = basePoints;
  
  // Add streak bonus
  score += streak * 10;
  
  // Add time bonus
  if (timeTaken < 5) {
    score += 20;
  }
  
  // Apply item multiplier
  const multiplier = itemBonuses.score_multiplier || 1.0;
  const itemBonus = Math.floor(score * (multiplier - 1.0));
  score = Math.floor(score * multiplier);
  
  return { score, itemBonus };
}
```

### Step 4: Display Item Bonuses

```javascript
<View style={styles.bonusDisplay}>
  <Text>Active Bonuses:</Text>
  {itemBonuses.score_multiplier > 1.0 && (
    <Text>⚔️ Score: +{((itemBonuses.score_multiplier - 1) * 100).toFixed(0)}%</Text>
  )}
  {itemBonuses.time_extension > 0 && (
    <Text>⏱️ Time: +{itemBonuses.time_extension}s</Text>
  )}
  {itemBonuses.xp_bonus > 0 && (
    <Text>✨ XP: +{(itemBonuses.xp_bonus * 100).toFixed(0)}%</Text>
  )}
</View>
```

---

## 🛠️ Creating Items with Effects

### Example Items:

```python
# Legendary Sword of Swift Answers
{
  "slug": "legendary_sword_swift_answers",
  "name": "Legendary Sword of Swift Answers",
  "slot": "weapon",
  "rarity": "legendary",
  "stats": {
    "score_multiplier": 1.35,
    "time_extension": 5,
    "streak_bonus": 15
  }
}

# Epic Helmet of Wisdom
{
  "slug": "epic_helmet_wisdom",
  "name": "Epic Helmet of Wisdom",
  "slot": "helmet",
  "rarity": "epic",
  "stats": {
    "score_multiplier": 1.15,
    "xp_bonus": 0.2,
    "perfect_bonus": 10
  }
}

# Rare Boots of Speed
{
  "slug": "rare_boots_speed",
  "name": "Rare Boots of Speed",
  "slot": "boots",
  "rarity": "rare",
  "stats": {
    "time_extension": 3,
    "time_bonus_multiplier": 1.2
  }
}

# Common Starter Sword
{
  "slug": "common_starter_sword",
  "name": "Common Starter Sword",
  "slot": "weapon",
  "rarity": "common",
  "stats": {
    "score_multiplier": 1.05
  }
}
```

### Seeding Items with Effects

```python
from app.domain.models import Item
from app.domain.enums import ItemSlot, ItemRarity

item = Item(
    id=uuid.uuid4(),
    slug="epic_sword_knowledge",
    name="Epic Sword of Knowledge",
    slot=ItemSlot.WEAPON,
    rarity=ItemRarity.EPIC,
    stats={
        "score_multiplier": 1.2,
        "time_extension": 4,
        "streak_bonus": 10
    }
)
```

---

## 📈 Balancing Guidelines

### Score Multipliers
- Should stack multiplicatively (3 items with 1.1x = 1.331x total)
- Keep total multiplier under 2.0x for fairness
- Higher rarities deserve better multipliers

### Time Extensions
- Should add linearly (3s + 2s = 5s total)
- Cap total extensions at ~15 seconds
- Be careful not to make questions too easy

### XP Bonuses
- Add linearly like time extensions
- Reward progression without being OP
- Legendary full set could give ~50% more XP

### Streak & Perfect Bonuses
- Reward skill and consistency
- Don't make them mandatory for competitiveness
- Should feel rewarding, not required

---

## 🎯 Testing Item Effects

1. **Equip items** in Character Customization
2. **Start a dungeon run**
3. **Check backend logs** for:
   ```
   User X has 3 equipped items with bonuses: {'score_multiplier': 1.25, 'time_extension': 5}
   ```
4. **Frontend should receive** bonuses in start response
5. **During gameplay**, verify:
   - Timer has extra seconds
   - Scores are higher with items equipped
   - Item bonuses display correctly
6. **After completion**, check scores are reasonable

---

## 🔍 Debugging

### Backend Logs
```bash
docker-compose logs api -f | grep -i "equipped items"
```

### Check What's Equipped
```bash
# Via API
GET /v1/inventory/equipped
```

### Verify Bonuses Applied
- Check `run.summary` in database for `equipped_items` and `total_bonuses`
- Frontend console should log received bonuses
- Score submission should include `item_bonus` field

---

## ✅ Summary

### Backend Changes:
- ✅ Added `StartRunResponse` with item bonuses
- ✅ Load equipped items when starting run
- ✅ Calculate and return total bonuses
- ✅ Accept `item_bonus` in score submission
- ✅ Store item info in run summary

### Frontend TODO:
- ⏳ Update `RunService.startRun()` to handle new response
- ⏳ Store and apply item bonuses during gameplay
- ⏳ Display active bonuses to player
- ⏳ Calculate item_bonus and include in submission
- ⏳ Show item effects on results screen

### Item Examples:
- ✅ Defined stat types and ranges
- ✅ Created example items
- ✅ Documented balancing guidelines

---

**Your items now matter in dungeons! Equip better gear to score higher, answer faster, and progress better!** ⚔️🛡️✨

