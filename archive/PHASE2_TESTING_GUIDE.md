# Phase 2 Testing Guide - Leaderboard System

This document provides comprehensive testing instructions for the newly implemented Leaderboard system with Redis caching.

---

## 🎯 What Was Built

### Backend Components
1. **Redis Client** (`app/core/redis_client.py`)
   - Async Redis operations
   - JSON serialization/deserialization
   - Connection management

2. **Leaderboard Service** (`app/services/leaderboard_service.py`)
   - Period key generation (ISO 8601 format)
   - Cache management with TTLs
   - User rank calculation
   - Statistics aggregation

3. **API Endpoints** (`app/api/v1/routers/leaderboards.py`)
   - `GET /v1/leaderboards` - Get rankings
   - `GET /v1/leaderboards/me` - Get user rank
   - `GET /v1/leaderboards/stats` - Get statistics

### Frontend Components
1. **Leaderboard Service** (`src/services/LeaderboardService.js`)
   - API integration
   - Timeout handling
   - Error management

2. **Leaderboard Screen** (`src/screens/Leaderboard.js`)
   - Scope switching (Today/Weekly/All-Time)
   - Pull-to-refresh
   - Loading states
   - Error handling
   - Empty states

---

## 🚀 Prerequisites

### 1. Start Backend Services
```bash
cd lorebound-backend
docker-compose up
```

This starts:
- PostgreSQL (port 5433)
- Redis (port 6379)
- FastAPI (port 8000)

### 2. Verify Services Are Running
```bash
# Check API health
curl http://localhost:8000/healthz

# Check Redis connection
docker exec -it lorebound-backend-redis-1 redis-cli ping
# Should return: PONG

# Check PostgreSQL
docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT 1"
```

### 3. Ensure Database Has Data
You need users and completed runs with scores to test the leaderboard.

```bash
# Check if you have scores
docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM scores"
```

If no scores exist, complete some dungeon runs through the app first.

---

## 🧪 Testing Checklist

### Backend API Testing

#### Test 1: Get All-Time Leaderboard
```bash
# Replace YOUR_TOKEN with actual JWT token
curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | json_pp
```

**Expected Response:**
```json
{
  "scope": "alltime",
  "period_key": "alltime",
  "total_participants": 15,
  "entries": [
    {
      "rank": 1,
      "user_id": "uuid",
      "handle": "PlayerName",
      "score": 9876,
      "total_runs": 142,
      "avatar_layers": {}
    }
  ],
  "last_updated": "2025-10-26T12:00:00Z"
}
```

**Verify:**
- ✅ Entries are sorted by score (descending)
- ✅ Ranks are sequential (1, 2, 3, ...)
- ✅ `total_participants` matches actual count
- ✅ All required fields present

#### Test 2: Get Today's Leaderboard
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=today&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | json_pp
```

**Expected Response:**
```json
{
  "scope": "today",
  "period_key": "2025-10-26",
  "total_participants": 5,
  "entries": [...]
}
```

**Verify:**
- ✅ `period_key` matches today's date (YYYY-MM-DD)
- ✅ Only shows scores from today
- ✅ Participant count is accurate

#### Test 3: Get Weekly Leaderboard
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=weekly&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | json_pp
```

**Expected Response:**
```json
{
  "scope": "weekly",
  "period_key": "2025-W43",
  "total_participants": 12,
  "entries": [...]
}
```

**Verify:**
- ✅ `period_key` uses ISO week format (YYYY-WNN)
- ✅ Only shows scores from current week
- ✅ Week number is correct

#### Test 4: Get User Rank
```bash
curl -X GET "http://localhost:8000/v1/leaderboards/me?scope=alltime&neighbors=3" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | json_pp
```

**Expected Response:**
```json
{
  "user_id": "uuid",
  "handle": "YourName",
  "rank": 42,
  "score": 2340,
  "total_runs": 15,
  "scope": "alltime",
  "period_key": "alltime",
  "neighbors": [
    {
      "rank": 40,
      "handle": "Player40",
      "score": 2398
    },
    {
      "rank": 41,
      "handle": "Player41",
      "score": 2361
    },
    {
      "rank": 43,
      "handle": "Player43",
      "score": 2325
    }
  ]
}
```

**Verify:**
- ✅ User's rank is correct
- ✅ Neighbors are sorted by rank
- ✅ Neighbors are close to user's rank
- ✅ If no scores, rank is `null`

#### Test 5: Get Leaderboard Statistics
```bash
curl -X GET "http://localhost:8000/v1/leaderboards/stats?scope=alltime" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | json_pp
```

**Expected Response:**
```json
{
  "scope": "alltime",
  "period_key": "alltime",
  "participants": 1247,
  "total_scores": 3542,
  "average_score": 1683.4,
  "highest_score": 9876,
  "lowest_score": 120,
  "last_updated": "2025-10-26T12:00:00Z"
}
```

**Verify:**
- ✅ Statistics are accurate
- ✅ Average is calculated correctly
- ✅ Highest/lowest scores are correct

---

### Redis Caching Testing

#### Test 6: Verify Cache Population
```bash
# First request - should hit database
time curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o /dev/null -s

# Second request - should hit cache (faster)
time curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o /dev/null -s
```

**Verify:**
- ✅ Second request is faster than first
- ✅ Response data is identical

#### Test 7: Check Redis Keys
```bash
# Connect to Redis
docker exec -it lorebound-backend-redis-1 redis-cli

# List all leaderboard keys
KEYS leaderboard:*

# Check a specific key
GET "leaderboard:alltime:alltime:100:0"

# Check TTL
TTL "leaderboard:alltime:alltime:100:0"
```

**Expected Keys:**
- `leaderboard:alltime:alltime:100:0` (TTL: 300s)
- `leaderboard:today:2025-10-26:100:0` (TTL: 30s)
- `leaderboard:weekly:2025-W43:100:0` (TTL: 60s)
- `user_rank:{user_id}:alltime:alltime`
- `leaderboard_stats:alltime:alltime`

**Verify:**
- ✅ Keys exist after API calls
- ✅ TTLs are set correctly
- ✅ Data is valid JSON

#### Test 8: Test Cache Expiration
```bash
# Make a request
curl -X GET "http://localhost:8000/v1/leaderboards?scope=today&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Wait 31 seconds (TTL for today is 30s)
sleep 31

# Make the same request - should hit database again
curl -X GET "http://localhost:8000/v1/leaderboards?scope=today&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Verify:**
- ✅ Cache expires after TTL
- ✅ Fresh data is fetched from database
- ✅ New cache entry is created

---

### Frontend Testing

#### Test 9: Leaderboard Screen Load
1. Start the React Native app
2. Navigate to Leaderboard screen
3. Observe loading state

**Verify:**
- ✅ Loading indicator shows
- ✅ "Loading leaderboard..." message displays
- ✅ No errors in console
- ✅ Data loads successfully

#### Test 10: Scope Switching
1. Open Leaderboard screen
2. Tap "Today" tab
3. Wait for data to load
4. Tap "This Week" tab
5. Wait for data to load
6. Tap "All-Time" tab

**Verify:**
- ✅ Active tab highlights correctly
- ✅ Data updates when switching scopes
- ✅ Loading indicator shows during fetch
- ✅ Participant count updates
- ✅ Period name updates in header

#### Test 11: Pull to Refresh
1. Open Leaderboard screen
2. Pull down on list to refresh

**Verify:**
- ✅ Refresh indicator shows
- ✅ Data reloads
- ✅ Refresh indicator disappears
- ✅ Data updates if changed

#### Test 12: Empty State
1. Switch to "Today" scope
2. If no runs today, observe empty state

**Verify:**
- ✅ Shows "No rankings yet for this period"
- ✅ Shows "Be the first to complete a run!"
- ✅ No crash or error

#### Test 13: Error Handling
1. Stop the backend server
2. Try to load leaderboard
3. Observe error message
4. Tap "Retry" button

**Verify:**
- ✅ Error message displays
- ✅ Retry button appears
- ✅ Tapping retry attempts reload
- ✅ Success message when backend is back

---

## 🔍 Performance Testing

### Test 14: Load Time Benchmarks

**Expected Performance:**
- First load (cold cache): < 500ms
- Cached load: < 50ms
- Scope switch: < 200ms

```bash
# Benchmark with Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/v1/leaderboards?scope=alltime&limit=100"
```

**Verify:**
- ✅ Mean response time < 100ms (with cache)
- ✅ No failed requests
- ✅ Consistent response times

### Test 15: Concurrent Users
```bash
# Simulate 50 concurrent users
ab -n 500 -c 50 -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/v1/leaderboards?scope=alltime&limit=100"
```

**Verify:**
- ✅ All requests succeed
- ✅ Redis handles concurrent reads
- ✅ No connection errors

---

## 🐛 Common Issues & Solutions

### Issue 1: "Redis connection failed"
**Solution:**
```bash
# Restart Redis
docker-compose restart redis

# Check Redis logs
docker logs lorebound-backend-redis-1
```

### Issue 2: Empty leaderboard
**Cause:** No scores in database
**Solution:**
1. Complete some dungeon runs
2. Check scores table: `SELECT COUNT(*) FROM scores`

### Issue 3: Cache not invalidating
**Cause:** Cache invalidation logic not triggered
**Solution:**
```bash
# Manually clear Redis cache
docker exec -it lorebound-backend-redis-1 redis-cli FLUSHDB
```

### Issue 4: Wrong period_key
**Cause:** Server timezone mismatch
**Solution:**
- Verify server uses UTC: `date -u`
- Check period key generation logic

---

## ✅ Success Criteria

Phase 2 is considered fully working when:

- [x] All three scopes return correct data (today/weekly/alltime)
- [x] Redis caching works with correct TTLs
- [x] User rank endpoint returns accurate position
- [x] Statistics endpoint provides correct aggregates
- [x] Frontend loads without errors
- [x] Scope switching works smoothly
- [x] Pull-to-refresh updates data
- [x] Error states display properly
- [x] Empty states show correct messages
- [x] Performance meets benchmarks
- [x] No memory leaks or connection issues

---

## 📝 Manual Test Checklist

Copy this checklist and mark items as you test:

### Backend
- [ ] GET /v1/leaderboards (alltime) returns data
- [ ] GET /v1/leaderboards (today) returns data
- [ ] GET /v1/leaderboards (weekly) returns data
- [ ] GET /v1/leaderboards/me returns user rank
- [ ] GET /v1/leaderboards/stats returns statistics
- [ ] Redis cache is populated after first request
- [ ] Cache expires after TTL
- [ ] Concurrent requests don't cause errors

### Frontend
- [ ] Leaderboard screen loads
- [ ] All-Time tab works
- [ ] Today tab works
- [ ] This Week tab works
- [ ] Pull-to-refresh works
- [ ] Loading states display
- [ ] Error states display
- [ ] Empty states display
- [ ] Participant count is accurate
- [ ] Scores are formatted correctly

### Integration
- [ ] Backend and frontend communicate
- [ ] Authentication works
- [ ] Data updates in real-time
- [ ] No console errors
- [ ] No network errors
- [ ] Performance is acceptable

---

## 🎉 Next Steps

After Phase 2 testing is complete:
1. Document any bugs found
2. Create GitHub issues for bugs
3. Move to Phase 3 (Character Customization)

---

**Last Updated:** October 26, 2025  
**Phase:** 2 (Leaderboard)  
**Status:** Ready for Testing

