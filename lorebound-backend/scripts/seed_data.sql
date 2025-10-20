-- Seed script for LoreBound content data

-- Insert sample dungeons
INSERT INTO dungeons (id, title, category, modifiers, content_version) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'Ancient History Depths', 'history', '{"description": "Journey through ancient civilizations", "difficulty": "medium", "estimated_duration": "15-20 minutes"}', 1),
('660e8400-e29b-41d4-a716-446655440001', 'Sports Arena Challenge', 'sports', '{"description": "Test your sports knowledge across all disciplines", "difficulty": "medium", "estimated_duration": "10-15 minutes"}', 1),
('770e8400-e29b-41d4-a716-446655440002', 'Musical Harmony Tower', 'music', '{"description": "Climb the tower of musical mastery", "difficulty": "easy", "estimated_duration": "12-18 minutes"}', 1),
('880e8400-e29b-41d4-a716-446655440003', 'Pop Culture Arcade', 'pop_culture', '{"description": "Navigate through decades of popular culture", "difficulty": "hard", "estimated_duration": "20-25 minutes"}', 1)
ON CONFLICT (id) DO NOTHING;

-- Insert dungeon tiers
INSERT INTO dungeon_tiers (id, dungeon_id, floor, boss_meta) VALUES 
('990e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', 1, '{"name": "Guardian of Knowledge", "description": "Ancient keeper of historical wisdom"}'),
('990e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 2, '{"name": "Pharaoh Spirit", "description": "Ruler of the ancient sands"}'),
('990e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 3, '{"name": "Roman Centurion", "description": "Elite warrior of the empire"}'),
('990e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440001', 1, '{"name": "Athletic Champion", "description": "Master of sports wisdom"}'),
('990e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440001', 2, '{"name": "Olympic Hero", "description": "Legend of competitive sports"}'),
('990e8400-e29b-41d4-a716-446655440005', '770e8400-e29b-41d4-a716-446655440002', 1, '{"name": "Melody Keeper", "description": "Guardian of ancient songs"}'),
('990e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440002', 2, '{"name": "Harmony Master", "description": "Composer of legendary pieces"}'),
('990e8400-e29b-41d4-a716-446655440007', '880e8400-e29b-41d4-a716-446655440003', 1, '{"name": "Trend Setter", "description": "Pioneer of cultural movements"}'),
('990e8400-e29b-41d4-a716-446655440008', '880e8400-e29b-41d4-a716-446655440003', 2, '{"name": "Media Mogul", "description": "Controller of entertainment empires"}')
ON CONFLICT (id) DO NOTHING;

-- Insert sample questions
INSERT INTO questions (id, dungeon_id, prompt, choices, answer_index, difficulty, tags) VALUES 
('aa0e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', 'Which ancient civilization built the pyramids of Giza?', '["Romans", "Egyptians", "Greeks", "Babylonians"]', 1, 'easy', '["history", "ancient", "egypt", "pyramids"]'),
('aa0e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Who was the first emperor of Rome?', '["Julius Caesar", "Augustus", "Nero", "Caligula"]', 1, 'medium', '["history", "ancient", "rome", "emperor"]'),
('aa0e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'The Colosseum was built in which city?', '["Athens", "Rome", "Alexandria", "Constantinople"]', 1, 'easy', '["history", "ancient", "rome", "architecture"]'),
('aa0e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440001', 'In which sport would you perform a slam dunk?', '["Soccer", "Tennis", "Basketball", "Volleyball"]', 2, 'easy', '["sports", "basketball", "basic"]'),
('aa0e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440001', 'How many players are on a basketball team on the court?', '["4", "5", "6", "7"]', 1, 'easy', '["sports", "basketball", "rules"]'),
('aa0e8400-e29b-41d4-a716-446655440005', '770e8400-e29b-41d4-a716-446655440002', 'Which composer wrote The Four Seasons?', '["Mozart", "Bach", "Vivaldi", "Beethoven"]', 2, 'medium', '["music", "classical", "composer", "baroque"]'),
('aa0e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440002', 'What instrument is Yo-Yo Ma famous for playing?', '["Violin", "Piano", "Cello", "Flute"]', 2, 'medium', '["music", "classical", "instruments"]'),
('aa0e8400-e29b-41d4-a716-446655440007', '880e8400-e29b-41d4-a716-446655440003', 'What TV show featured the characters Ross, Rachel, and Monica?', '["Seinfeld", "Friends", "Cheers", "Frasier"]', 1, 'easy', '["tv", "sitcom", "90s", "friends"]'),
('aa0e8400-e29b-41d4-a716-446655440008', '880e8400-e29b-41d4-a716-446655440003', 'Which movie won the Academy Award for Best Picture in 1994?', '["Forrest Gump", "Pulp Fiction", "The Lion King", "Speed"]', 0, 'hard', '["movies", "oscars", "90s"]]')
ON CONFLICT (id) DO NOTHING;

-- Verify the data
SELECT 'Dungeons inserted:' as info, count(*) as count FROM dungeons;
SELECT 'Dungeon tiers inserted:' as info, count(*) as count FROM dungeon_tiers;
SELECT 'Questions inserted:' as info, count(*) as count FROM questions;
