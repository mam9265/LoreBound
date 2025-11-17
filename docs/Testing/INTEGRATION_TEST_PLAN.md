# Integration Test Plan - Phase 1 & 2

## 🎯 Objective

Test Phase 1 (Dungeon Runs) and Phase 2 (Leaderboard) to ensure:
- All backend services start correctly
- API endpoints work as expected
- Frontend can communicate with backend
- Data flows correctly between systems
- No critical bugs or errors

---

## 📋 Pre-Test Checklist

### 1. Backend Requirements
- [ ] Docker Desktop is running
- [ ] Ports 5433, 6379, 8000 are available
- [ ] `lorebound-backend/.env` file exists with correct config
- [ ] Database migrations are ready to run

### 2. Frontend Requirements
- [ ] Node.js installed
- [ ] Dependencies installed (`npm install`)
- [ ] React Native environment configured
- [ ] API_BASE_URL configured correctly

---

## 🚀 Step-by-Step Testing

## Part 1: Backend Setup & Verification

### Step 1: Start Backend Services
```bash
cd lorebound-backend
docker-compose up -d
```

**Expected Output:**
```
✓ Network lorebound-backend_default  Created
✓ Container lorebound-backend-db-1    Started
✓ Container lorebound-backend-redis-1 Started
✓ Container lorebound-backend-api-1   Started
```

**Verify:**
```bash
docker-compose ps
```

All services should show "Up" status.

### Step 2: Check Service Health

**PostgreSQL:**
```bash
docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT 1"
```
Expected: `(1 row)` - Database is accessible

**Redis:**
```bash
docker exec -it lorebound-backend-redis-1 redis-cli ping
```
Expected: `PONG` - Redis is responsive

**FastAPI:**
```bash
curl http://localhost:8000/healthz
```
Expected: JSON response with `"status":"healthy"`

### Step 3: Run Database Migrations
```bash
# Check current migration status
docker-compose exec api alembic current

# Run migrations
docker-compose exec api alembic upgrade head

# Verify migration completed
docker-compose exec api alembic current
```

**Verify:**
- Migration runs without errors
- Database schema includes: runs, scores, leaderboard_snapshots tables

### Step 4: Check Database Schema
```bash
docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound -c "\dt"
```

**Required Tables:**
- users
- profiles
- runs
- scores
- dungeons
- questions
- leaderboard_snapshots
- items
- inventory
- achievements

### Step 5: Verify Redis Connection
```bash
# Check Redis info
docker exec -it lorebound-backend-redis-1 redis-cli INFO server

# Test set/get
docker exec -it lorebound-backend-redis-1 redis-cli SET test_key "test_value"
docker exec -it lorebound-backend-redis-1 redis-cli GET test_key
```

**Expected:** Can set and retrieve values

---

## Part 2: Backend API Testing

### Step 6: Get Authentication Token

**Option A: Using existing user**
```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "your_password"
  }'
```

**Option B: Register new user**
```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "handle": "TestPlayer"
  }'
```

**Save the token:**
```bash
export TOKEN="your_access_token_here"
```

### Step 7: Test Phase 1 - Dungeon Runs

**Test 7a: Get Dungeons**
```bash
curl -X GET "http://localhost:8000/v1/content/dungeons" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- Returns list of dungeons
- Each has: id, title, category
- No errors

**Test 7b: Start a Run**
```bash
# First, get a dungeon ID from previous response
DUNGEON_ID="paste_dungeon_id_here"

curl -X POST "http://localhost:8000/v1/runs/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dungeon_id\": \"$DUNGEON_ID\",
    \"floor\": 1
  }"
```

**Verify:**
- Returns run object with: id, session_token, status: "in_progress"
- Save the run_id and session_token

**Test 7c: Get Questions**
```bash
curl -X GET "http://localhost:8000/v1/content/questions?dungeon_id=$DUNGEON_ID&count=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- Returns 10 questions
- Each has: id, prompt, choices, difficulty
- answer_index is present

**Test 7d: Submit Run**
```bash
RUN_ID="paste_run_id_here"

curl -X POST "http://localhost:8000/v1/runs/$RUN_ID/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "turn_data": [
      {
        "i": 0,
        "qid": "question_uuid_here",
        "a": 1,
        "c": true,
        "t": 2500,
        "ts": 1699999990000,
        "h": "test_signature"
      }
    ],
    "scores": [
      {
        "points": 100,
        "answer_time": 2.5,
        "is_correct": true,
        "streak_bonus": 10,
        "time_bonus": 5
      }
    ],
    "client_signature": "test_aggregate_sig"
  }'
```

**Verify:**
- Run status changes to "completed"
- total_score is calculated
- completed_at timestamp is set

**Test 7e: Get Run History**
```bash
curl -X GET "http://localhost:8000/v1/runs?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- Returns list of runs
- Most recent run is at the top
- Each has: id, dungeon_id, status, total_score

**Test 7f: Get Run Stats**
```bash
curl -X GET "http://localhost:8000/v1/runs/stats/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- Returns: total_runs, total_score, average_score, best_score
- Stats match completed runs

### Step 8: Test Phase 2 - Leaderboard

**Test 8a: Get All-Time Leaderboard**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Verify:**
- Returns entries sorted by score
- Each entry has: rank, user_id, handle, score, total_runs
- total_participants is accurate
- period_key is "alltime"

**Test 8b: Get Today's Leaderboard**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=today&limit=10" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Verify:**
- period_key matches today's date (YYYY-MM-DD)
- Only shows scores from today
- Entries are sorted correctly

**Test 8c: Get Weekly Leaderboard**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=weekly&limit=10" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Verify:**
- period_key uses ISO week format (YYYY-WNN)
- Shows scores from current week
- Participant count is accurate

**Test 8d: Get Your Rank**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards/me?scope=alltime&neighbors=3" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Verify:**
- Returns your rank (or null if no scores)
- Shows 3 neighbors above and below
- Neighbors are sorted by rank
- Your score matches latest run

**Test 8e: Get Leaderboard Stats**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards/stats?scope=alltime" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Verify:**
- Returns: participants, average_score, highest_score, lowest_score
- Statistics are accurate

**Test 8f: Verify Redis Caching**
```bash
# Make the same request twice and time them
time curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer $TOKEN" -o /dev/null -s

time curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer $TOKEN" -o /dev/null -s
```

**Verify:**
- Second request is faster
- Check Redis has the cache:
```bash
docker exec -it lorebound-backend-redis-1 redis-cli KEYS "leaderboard:*"
```

---

## Part 3: Frontend Testing

### Step 9: Start Frontend

```bash
cd lorebound
npm start
```

In another terminal:
```bash
npm run android  # or npm run ios
```

### Step 10: Test Phase 1 Screens

**Test 10a: RunGameplay Screen**
1. Navigate to dungeon selection
2. Start a new run
3. Verify:
   - [ ] Timer starts
   - [ ] Questions load
   - [ ] Can select answers
   - [ ] Score updates
   - [ ] Lives system works
   - [ ] Can complete run

**Test 10b: RunResults Screen**
1. Complete a run
2. Verify:
   - [ ] Shows final score
   - [ ] Shows statistics
   - [ ] Shows correct/incorrect breakdown
   - [ ] "Play Again" button works
   - [ ] "View History" button works

**Test 10c: RunHistory Screen**
1. Navigate to run history
2. Verify:
   - [ ] Shows list of past runs
   - [ ] Shows scores and dates
   - [ ] Can tap to view details
   - [ ] Pull-to-refresh works
   - [ ] Pagination works

### Step 11: Test Phase 2 Screens

**Test 11a: Leaderboard Screen**
1. Navigate to Leaderboard
2. Verify:
   - [ ] Loads without errors
   - [ ] Shows ranked players
   - [ ] Shows scores
   - [ ] Shows participant count

**Test 11b: Scope Switching**
1. Tap "Today" tab
2. Verify data updates
3. Tap "This Week" tab
4. Verify data updates
5. Tap "All-Time" tab
6. Verify:
   - [ ] Active tab highlights correctly
   - [ ] Data is different for each scope
   - [ ] Loading states show during switch
   - [ ] No errors in console

**Test 11c: Pull-to-Refresh**
1. Pull down on leaderboard
2. Verify:
   - [ ] Refresh indicator shows
   - [ ] Data reloads
   - [ ] Indicator disappears

**Test 11d: Error Handling**
1. Stop backend server
2. Try to load leaderboard
3. Verify:
   - [ ] Error message displays
   - [ ] Retry button appears
4. Restart backend
5. Tap retry
6. Verify:
   - [ ] Data loads successfully

---

## Part 4: Integration Testing

### Step 12: Complete Flow Test

**Flow:** Start Run → Complete Run → See Leaderboard Update

1. Note your current rank (if any)
2. Start a new dungeon run
3. Answer questions correctly to get a high score
4. Complete the run
5. Navigate to leaderboard
6. Pull to refresh
7. Verify:
   - [ ] Your rank updated (if score improved)
   - [ ] New score is reflected
   - [ ] total_runs incremented
   - [ ] Stats are accurate

### Step 13: Cache Invalidation Test

1. Complete a run with a good score
2. Immediately check leaderboard
3. Verify:
   - [ ] Leaderboard shows updated ranking
   - [ ] Cache was invalidated
   - [ ] New data is fresh

### Step 14: Multi-Scope Test

1. Complete a run today
2. Check "Today" leaderboard - should show your run
3. Check "Weekly" leaderboard - should show your run
4. Check "All-Time" leaderboard - should show your run
5. Verify:
   - [ ] Same run appears in all scopes
   - [ ] Ranks may differ between scopes
   - [ ] Scores are consistent

---

## 🐛 Known Issues to Check

### Backend Issues
- [ ] Database migrations run cleanly
- [ ] Redis connects without errors
- [ ] No 500 errors in API logs
- [ ] Authentication works correctly
- [ ] Anti-cheat validation doesn't reject valid submissions

### Frontend Issues
- [ ] API_BASE_URL is correct
- [ ] Authentication token persists
- [ ] Navigation works between screens
- [ ] No React Native warnings
- [ ] Network requests timeout appropriately

---

## 📝 Test Results Template

Copy this and fill in as you test:

### Backend Services
- [ ] PostgreSQL: PASS / FAIL
- [ ] Redis: PASS / FAIL
- [ ] FastAPI: PASS / FAIL
- [ ] Migrations: PASS / FAIL

### Phase 1 API
- [ ] Start Run: PASS / FAIL
- [ ] Submit Run: PASS / FAIL
- [ ] Get History: PASS / FAIL
- [ ] Get Stats: PASS / FAIL

### Phase 2 API
- [ ] Get Leaderboard (all scopes): PASS / FAIL
- [ ] Get User Rank: PASS / FAIL
- [ ] Get Stats: PASS / FAIL
- [ ] Redis Caching: PASS / FAIL

### Frontend Phase 1
- [ ] RunGameplay: PASS / FAIL
- [ ] RunResults: PASS / FAIL
- [ ] RunHistory: PASS / FAIL

### Frontend Phase 2
- [ ] Leaderboard Load: PASS / FAIL
- [ ] Scope Switching: PASS / FAIL
- [ ] Pull-to-Refresh: PASS / FAIL

### Integration
- [ ] Complete Flow: PASS / FAIL
- [ ] Cache Invalidation: PASS / FAIL

---

## 🔧 Debugging Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Just API
docker-compose logs -f api

# Just Redis
docker-compose logs -f redis
```

### Check Database
```bash
# Connect to DB
docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound

# Check runs
SELECT COUNT(*) FROM runs;

# Check scores
SELECT COUNT(*) FROM scores;

# Check recent scores
SELECT u.email, s.score, s.created_at 
FROM scores s 
JOIN users u ON s.user_id = u.id 
ORDER BY s.created_at DESC 
LIMIT 10;
```

### Check Redis
```bash
# Connect to Redis
docker exec -it lorebound-backend-redis-1 redis-cli

# List all keys
KEYS *

# Check specific cache
GET "leaderboard:alltime:alltime:100:0"

# Clear all cache
FLUSHDB
```

---

## ✅ Success Criteria

Testing is complete when:
- [ ] All backend services start successfully
- [ ] All API endpoints return expected data
- [ ] Frontend loads without errors
- [ ] Complete flow works end-to-end
- [ ] Redis caching is working
- [ ] No critical bugs found
- [ ] Any minor bugs are documented

---

**Ready to begin testing!** 🧪

Start with Part 1, Step 1 and work through systematically.

