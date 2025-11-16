-- SQL script to create test items with effects
-- Run this in PostgreSQL to add items you can equip and test

-- Legendary Sword of Power (35% score bonus, +5 seconds, +15 streak)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'legendary_sword_power',
  'Legendary Sword of Power',
  'weapon',
  'legendary',
  '{"score_multiplier": 1.35, "time_extension": 5, "streak_bonus": 15}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Epic Helmet of Wisdom (15% score bonus, +20% XP)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'epic_helmet_wisdom',
  'Epic Helmet of Wisdom',
  'helmet',
  'epic',
  '{"score_multiplier": 1.15, "xp_bonus": 0.2}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Epic Armor of Fortitude (10% score bonus, +3 seconds)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'epic_armor_fortitude',
  'Epic Armor of Fortitude',
  'armor',
  'epic',
  '{"score_multiplier": 1.1, "time_extension": 3}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Rare Boots of Speed (+3 seconds, +10% XP)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'rare_boots_speed',
  'Rare Boots of Speed',
  'boots',
  'rare',
  '{"time_extension": 3, "xp_bonus": 0.1}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Rare Shield of Protection (+5% score, +10 perfect bonus)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'rare_shield_protection',
  'Rare Shield of Protection',
  'shield',
  'rare',
  '{"score_multiplier": 1.05, "perfect_bonus": 10}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Uncommon Ring of Knowledge (+5% XP, +2 seconds)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'uncommon_ring_knowledge',
  'Uncommon Ring of Knowledge',
  'ring',
  'uncommon',
  '{"xp_bonus": 0.05, "time_extension": 2}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Uncommon Amulet of Focus (+5 streak bonus)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'uncommon_amulet_focus',
  'Uncommon Amulet of Focus',
  'amulet',
  'uncommon',
  '{"streak_bonus": 5}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Common Starter Sword (5% score bonus)
INSERT INTO items (id, slug, name, slot, rarity, stats)
VALUES (
  gen_random_uuid(),
  'common_starter_sword',
  'Common Starter Sword',
  'weapon',
  'common',
  '{"score_multiplier": 1.05}'::jsonb
) ON CONFLICT (slug) DO UPDATE SET
  stats = EXCLUDED.stats;

-- Display created items
SELECT 
  slug,
  name,
  slot,
  rarity,
  stats
FROM items
WHERE slug IN (
  'legendary_sword_power',
  'epic_helmet_wisdom',
  'epic_armor_fortitude',
  'rare_boots_speed',
  'rare_shield_protection',
  'uncommon_ring_knowledge',
  'uncommon_amulet_focus',
  'common_starter_sword'
);

-- To add these to YOUR inventory, run:
-- (Replace YOUR_USER_ID with your actual user ID from the users table)

/*
INSERT INTO inventory (user_id, item_id, equipped, acquired_at)
SELECT 
  'YOUR_USER_ID'::uuid,
  id,
  false,  -- Not equipped by default
  NOW()
FROM items
WHERE slug IN (
  'legendary_sword_power',
  'epic_helmet_wisdom',
  'epic_armor_fortitude',
  'rare_boots_speed',
  'rare_shield_protection',
  'uncommon_ring_knowledge',
  'uncommon_amulet_focus',
  'common_starter_sword'
)
ON CONFLICT (user_id, item_id) DO NOTHING;
*/

