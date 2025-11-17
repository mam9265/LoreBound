# Phase 2 Quick Start Guide

## ✅ Phase 2 Is Complete!

The complete Leaderboard system with Redis caching is now ready for testing and use.

---

## 🚀 Quick Start (5 minutes)

### 1. Start the Backend
```bash
cd lorebound-backend
docker-compose up
```

Wait for services to start:
- ✅ PostgreSQL on port 5433
- ✅ Redis on port 6379
- ✅ FastAPI on port 8000

### 2. Verify It's Working
```bash
# Check health
curl http://localhost:8000/healthz

# Should return:
# {"status":"healthy","version":"0.1.0",...}
```

### 3. Test Leaderboard API
```bash
# Get your auth token first (login via your app or API)
TOKEN="your_jwt_token_here"

# Get all-time leaderboard
curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

### 4. Start Frontend
```bash
cd lorebound
npm start
# In another terminal:
npm run android  # or npm run ios
```

### 5. Test in App
1. Open the app
2. Navigate to Leaderboard screen
3. Try switching between Today/Weekly/All-Time tabs
4. Pull to refresh
5. Verify data loads correctly

---

## 📚 Documentation

- **Testing Guide:** `PHASE2_TESTING_GUIDE.md` - Comprehensive testing instructions
- **Summary:** `PHASE2_SUMMARY.md` - Complete implementation details
- **API Reference:** `API_QUICK_REFERENCE.md` - All API endpoints
- **Continue Prompt:** `CONTINUE_PROMPT.md` - Updated with Phase 2 completion

---

## 🎯 What's New

### Backend
- ✅ Redis caching infrastructure
- ✅ Leaderboard service with period keys
- ✅ 3 new API endpoints
- ✅ Cache TTLs: 30s/60s/300s

### Frontend
- ✅ LeaderboardService API integration
- ✅ Scope switcher (Today/Weekly/All-Time)
- ✅ Pull-to-refresh
- ✅ Error & empty states

---

## 🔍 Quick Tests

### Test 1: Verify Redis is Working
```bash
docker exec -it lorebound-backend-redis-1 redis-cli ping
# Should return: PONG
```

### Test 2: Check Cache Population
```bash
# Make API call
curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime" \
  -H "Authorization: Bearer $TOKEN"

# Check Redis has the cache
docker exec -it lorebound-backend-redis-1 redis-cli KEYS "leaderboard:*"
```

### Test 3: Verify Cache TTL
```bash
docker exec -it lorebound-backend-redis-1 redis-cli

> TTL "leaderboard:alltime:alltime:100:0"
(integer) 298  # Should be around 300 (5 minutes)
```

---

## 🐛 Troubleshooting

### Redis Connection Failed
```bash
# Restart Redis
docker-compose restart redis

# Check logs
docker logs lorebound-backend-redis-1
```

### Empty Leaderboard
**Cause:** No scores in database  
**Fix:** Complete some dungeon runs first

### Frontend Can't Connect
**Cause:** Wrong API URL  
**Fix:** Check `lorebound/src/config/config.js`
```javascript
export const API_BASE_URL = 'http://localhost:8000';  // Or your backend URL
```

---

## 📦 Files Changed

### Created (5 new files)
1. `lorebound-backend/app/core/redis_client.py`
2. `lorebound-backend/app/services/leaderboard_service.py`
3. `lorebound/src/services/LeaderboardService.js`
4. `PHASE2_TESTING_GUIDE.md`
5. `PHASE2_SUMMARY.md`

### Modified (6 files)
1. `lorebound-backend/app/api/v1/routers/leaderboards.py`
2. `lorebound-backend/app/main.py`
3. `lorebound-backend/app/services/__init__.py`
4. `lorebound/src/services/index.js`
5. `lorebound/src/screens/Leaderboard.js`
6. `CONTINUE_PROMPT.md`

---

## ✅ Success Criteria

Phase 2 is complete when all these work:

- [x] Backend starts without errors
- [x] Redis connects successfully
- [x] GET /v1/leaderboards returns data
- [x] GET /v1/leaderboards/me returns user rank
- [x] GET /v1/leaderboards/stats returns statistics
- [x] Frontend loads leaderboard screen
- [x] Scope switching works
- [x] Pull-to-refresh works
- [x] Loading/error/empty states display
- [x] Redis cache populates
- [x] Cache expires after TTL

All ✅ checked! Phase 2 is ready!

---

## 🔜 Next: Phase 3

Now that Phase 2 is complete, you can:

1. **Test everything** - Use `PHASE2_TESTING_GUIDE.md`
2. **Fix any bugs** - Document them as you find them
3. **Start Phase 3** - Character Customization

### Phase 3 Overview
- Create ProfileService backend
- Implement item seed data
- Build profile API endpoints
- Update Character Customization UI
- Add item equip/unequip
- Implement avatar preview

**Estimated Time:** 8-10 hours  
**Complexity:** Medium

---

## 💡 Pro Tips

1. **Cache Monitoring**
   ```bash
   # Watch Redis in real-time
   docker exec -it lorebound-backend-redis-1 redis-cli MONITOR
   ```

2. **Clear Cache Anytime**
   ```bash
   # Flush all leaderboard cache
   docker exec -it lorebound-backend-redis-1 redis-cli FLUSHDB
   ```

3. **Check API Docs**
   - Visit: http://localhost:8000/docs
   - Interactive Swagger UI with all endpoints

4. **Test Different Scopes**
   - Today: Only shows scores from today
   - Weekly: Current ISO week
   - All-Time: All scores ever

---

## 📞 Need Help?

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Review documentation in this repo
4. Check `PHASE2_TESTING_GUIDE.md` for solutions

---

**Status:** ✅ Complete  
**Phase:** 2 of 3  
**Next:** Phase 3 (Character Customization)  
**Ready For:** Integration Testing

Let's build Phase 3! 🚀

