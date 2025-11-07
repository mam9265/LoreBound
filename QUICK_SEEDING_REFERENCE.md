# Quick Seeding Reference Card 🚀

**TL;DR**: Populate LoreBound database with trivia questions from OpenTDB API

---

## ⚡ Quick Start (Copy & Paste)

```bash
# 1. Navigate to backend
cd lorebound-backend

# 2. Make sure services are running
docker-compose ps

# 3. Seed the database (50 questions per category)
docker-compose exec api python -m scripts.populate_questions

# 4. Verify questions were added
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions;"
```

**Done!** ✅ Your database now has ~200-300 questions.

---

## 📝 Common Commands

### Seed All Categories
```bash
docker-compose exec api python -m scripts.populate_questions
```
*Adds 50 questions per category (~3-5 minutes)*

### Seed Specific Category
```bash
# History
docker-compose exec api python -m scripts.populate_questions --category history --count 100

# Music
docker-compose exec api python -m scripts.populate_questions --category music --count 100

# Sports
docker-compose exec api python -m scripts.populate_questions --category sports --count 100
```

### Large Production Seed
```bash
docker-compose exec api python -m scripts.populate_questions --count 200
```
*Adds 200 questions per category (~15 minutes)*

---

## 🔍 Check Results

### Quick Count
```bash
docker-compose exec db psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM questions;"
```

### By Difficulty
```bash
docker-compose exec db psql -U postgres -d lorebound -c "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty;"
```

### By Category
```bash
docker-compose exec db psql -U postgres -d lorebound -c "SELECT d.category, COUNT(q.id) FROM questions q JOIN dungeons d ON q.dungeon_id = d.id GROUP BY d.category;"
```

---

## 🎯 Recommended Amounts

| Environment | Questions/Category | Total Questions | Time |
|-------------|-------------------|-----------------|------|
| **Testing** | 50 | ~200 | 3-5 min |
| **Development** | 100 | ~400-600 | 8-10 min |
| **Production** | 200+ | ~800-1200 | 15-20 min |

---

## 🐛 Common Issues

### "Daily challenge only shows 2 questions"
```bash
# Need more HARD questions
docker-compose exec api python -m scripts.populate_questions --count 150
```

### "Script is very slow"
**This is normal!** OpenTDB rate limit = 1 request per 5 seconds.

### "Network request failed"
```bash
# Test API connection
curl "https://opentdb.com/api.php?amount=1&type=multiple"
```

---

## 📋 Available Categories

```
history, music, sports, pop_culture,
science, geography, film, television,
video_games, books, art, nature
```

---

## ⏱️ Important Note

**OpenTDB Rate Limit**: 1 request per 5 seconds

- Scripts automatically respect this
- Seeding takes time - be patient!
- Progress is shown as it runs

---

## ✅ Success Check

```bash
# Should have:
# - Total questions > 200
# - Hard questions > 50
# - Questions in all categories

docker-compose exec db psql -U postgres -d lorebound -c "
SELECT 
    d.category,
    COUNT(CASE WHEN q.difficulty = 'hard' THEN 1 END) as hard_questions,
    COUNT(*) as total_questions
FROM questions q
JOIN dungeons d ON q.dungeon_id = d.id
GROUP BY d.category;"
```

---

## 📚 Full Guide

For detailed information, see: `DATABASE_SEEDING_GUIDE.md`

---

**Questions?** Check logs:
```bash
docker-compose logs -f api | grep "question"
```

