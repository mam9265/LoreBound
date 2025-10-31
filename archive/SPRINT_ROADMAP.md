# Sprint Roadmap: Dungeon Runs, Leaderboard & Character Customization

**Sprint Goal:** Add full Dungeon Run gameplay, Leaderboard functionality, and Character Customization system

**Last Updated:** October 26, 2025

---

## 📊 Progress Overview

### Feature Status
- [x] **Dungeon Runs** - 95% Complete (Backend ✅, Frontend ✅, Testing Needed)
- [ ] **Leaderboard** - 50% Complete (Backend Done, Frontend Integration Needed)
- [ ] **Character Customization** - 30% Complete (Frontend UI Done, Backend Needed)

### Overall Sprint Progress: 60%

**🎉 Phase 1 Complete!** All Dungeon Runs services are operational. See `PHASE1_COMPLETE.md` for details.

---

## 🎯 Feature 1: Dungeon Runs

### Overview
Enable users to start dungeon runs, answer trivia questions, and track their progress through floors with real-time scoring.

### Backend Status ✅ MOSTLY COMPLETE
The backend already has most infrastructure in place:

**Existing Components:**
- ✅ `Run` model with seed, timestamps, summary, signature
- ✅ `Score` model tracking performance metrics
- ✅ `RunRepository` with CRUD operations
- ✅ `RunService` (needs review)
- ✅ API endpoints: `/v1/runs/start`, `/v1/runs/{id}/submit`, `/v1/runs/`, `/v1/runs/{id}`
- ✅ Anti-cheat system with HMAC signatures
- ✅ Run statistics endpoint `/v1/runs/stats/me`

**Backend Tasks:**
- [x] **B1.1** Review and test `RunService` for completeness ✅
- [x] **B1.2** Verify anti-cheat implementation works correctly ✅
- [x] **B1.3** Add dungeon-specific run statistics endpoint ✅
- [x] **B1.4** Add run abandonment logic (partially exists) ✅
- [x] **B1.5** Test run flow end-to-end with seed-based question generation ✅

### Frontend Status ⚠️ NEEDS WORK
The frontend has basic dungeon selection but no run gameplay.

**Existing Components:**
- ✅ `DungeonSelect.js` screen (basic UI)
- ✅ Basic dungeon screens (SportDungeon, MusicDungeon, etc.)
- ✅ API service structure in `src/services/api.js`

**Frontend Tasks:**
- [x] **F1.1** Create `RunGameplay.js` screen for active dungeon runs ✅
  - Question display with timer ✅
  - Answer selection UI ✅
  - Progress indicators (floor, lives, score) ✅
  - Turn-by-turn tracking ✅
  
- [x] **F1.2** Create `RunService.js` in `src/services/` ✅
  - `startRun(dungeonId)` - Start new run ✅
  - `submitRun(runId, turnData, scores, signature)` - Submit completed run ✅
  - `abandonRun(runId)` - Abandon active run ✅
  - `getUserRuns(limit, offset)` - Get run history ✅
  - `getRunById(runId)` - Get specific run details ✅
  - `getUserStats()` - Get user statistics ✅
  
- [x] **F1.3** Create `RunHistory.js` screen ✅
  - Display user's past runs ✅
  - Show scores, dates, dungeons played ✅
  - Filter by dungeon, date range ✅
  - Pull to refresh ✅
  
- [ ] **F1.4** Update dungeon screens to start runs (NEXT: Integration step)
  - Replace static content with run initialization
  - Pass dungeon metadata to gameplay screen
  
- [x] **F1.5** Create `RunResultsScreen.js` ✅
  - Display final score and statistics ✅
  - Show rank if available ✅
  - Share/replay options ✅
  - Navigate to leaderboard ✅
  
- [x] **F1.6** Add run state management ✅
  - Track active run in component state ✅
  - Turn-by-turn data tracking ✅
  - Handle app backgrounding during runs (basic) ✅
  
- [x] **F1.7** Implement anti-cheat client side ✅
  - Generate HMAC signatures for turns ✅
  - Calculate client signature for submission ✅
  - Store session token securely ✅

**Integration Tasks:**
- [ ] **I1.1** Wire up `DungeonSelect` → `RunGameplay` flow (NEXT STEP)
- [ ] **I1.2** Test complete run cycle: start → play → submit (NEXT STEP)
- [x] **I1.3** Handle network errors and retries ✅
- [x] **I1.4** Add loading states and animations ✅
- [ ] **I1.5** Test run recovery after app crash/closure (Future enhancement)

---

## 🏆 Feature 2: Leaderboard

### Overview
Real-time leaderboards showing top players with daily, weekly, and all-time rankings.

### Backend Status ✅ MOSTLY COMPLETE
Strong foundation already exists:

**Existing Components:**
- ✅ `LeaderboardSnapshot` model
- ✅ `LeaderboardRepository` with ranking logic
- ✅ `LeaderboardScope` enum (DAILY, WEEKLY, ALLTIME)
- ✅ Methods for top scores, user rank, neighbors
- ✅ Redis infrastructure ready (docker-compose)

**Backend Tasks:**
- [ ] **B2.1** Create `LeaderboardService` in `app/services/`
  - `get_leaderboard(scope, period_key, limit, offset)`
  - `get_user_rank(user_id, scope, period_key)`
  - `get_user_neighbors(user_id, scope, neighbors_count)`
  - `update_leaderboard_cache(score)` - Redis update
  
- [ ] **B2.2** Create leaderboard API endpoints in `app/api/v1/routers/leaderboards.py`
  - `GET /v1/leaderboards` - Get leaderboard (query params: scope, limit, offset)
  - `GET /v1/leaderboards/me` - Get user's rank and neighbors
  - `GET /v1/leaderboards/stats` - Get leaderboard statistics
  
- [ ] **B2.3** Implement Redis leaderboard caching
  - Sorted sets for each scope (daily, weekly, alltime)
  - Auto-update on score submission
  - Background job to sync Redis → PostgreSQL snapshots
  
- [ ] **B2.4** Create schemas in `app/schemas/leaderboard.py`
  - `LeaderboardEntryResponse` - Single leaderboard entry
  - `LeaderboardResponse` - Full leaderboard with metadata
  - `UserRankResponse` - User rank with neighbors
  
- [ ] **B2.5** Add leaderboard reset job for daily/weekly cycles
  - Celery task in `app/jobs/tasks/`
  - Create snapshots before reset
  - Schedule daily at midnight UTC

### Frontend Status ⚠️ NEEDS INTEGRATION
UI exists but needs API connection:

**Existing Components:**
- ✅ `Leaderboard.js` with mock data and UI
- ✅ Pull-to-refresh implemented
- ✅ Rank, player name, score display
- ✅ Avatar placeholders

**Frontend Tasks:**
- [ ] **F2.1** Update `Leaderboard.js` to use real API
  - Replace mock data with API calls
  - Add scope selector (Daily/Weekly/All-Time)
  - Implement pagination/infinite scroll
  - Show loading skeleton
  
- [ ] **F2.2** Create `LeaderboardService.js` in `src/services/`
  - `getLeaderboard(scope, limit, offset)`
  - `getUserRank(scope)`
  - `getLeaderboardStats(scope)`
  
- [ ] **F2.3** Add user's position highlight
  - Scroll to user position on load
  - Different styling for current user
  - Show rank change indicators (up/down)
  
- [ ] **F2.4** Add filters and tabs
  - Tab bar for Daily/Weekly/All-Time
  - Filter by dungeon type (optional)
  - Show period info (e.g., "Week 43, 2025")
  
- [ ] **F2.5** Add leaderboard entry modal
  - Tap entry to view player profile
  - Show user stats, badges, equipment
  
- [ ] **F2.6** Connect leaderboard to run results
  - Show updated rank after completing run
  - "View on Leaderboard" button

**Integration Tasks:**
- [ ] **I2.1** Test leaderboard with real user data
- [ ] **I2.2** Verify rank calculations are accurate
- [ ] **I2.3** Test scope switching and data refresh
- [ ] **I2.4** Performance test with large leaderboards (1000+ users)

---

## 🎨 Feature 3: Character Customization

### Overview
Allow users to customize their character's appearance with unlockable equipment and cosmetics.

### Backend Status ⚠️ NEEDS EXPANSION
Basic inventory system exists:

**Existing Components:**
- ✅ `Item` model with slot, rarity, stats
- ✅ `Inventory` model linking users to items
- ✅ `Profile` model with `avatar_layers` JSON field
- ✅ `InventoryRepository` (needs review)
- ✅ Item slots enum: HELMET, ARMOR, WEAPON, SHIELD

**Backend Tasks:**
- [ ] **B3.1** Create comprehensive item seed data
  - Generate items for each slot (helmet, armor, weapon, shield)
  - Define rarity levels (common, rare, epic, legendary)
  - Add stats and visual identifiers
  - Create script: `scripts/seed_items_data.py`
  
- [ ] **B3.2** Create `ProfileService` in `app/services/`
  - `get_user_profile(user_id)` - Get profile with equipped items
  - `update_avatar_layers(user_id, layers)` - Update customization
  - `get_unlocked_items(user_id)` - Get user's inventory
  - `equip_item(user_id, item_id, slot)` - Equip item
  - `unequip_item(user_id, slot)` - Remove equipped item
  
- [ ] **B3.3** Create profile/customization endpoints
  - `GET /v1/profile` - Get user profile and equipped items
  - `PUT /v1/profile/avatar` - Update avatar customization
  - `GET /v1/inventory/items` - Get all owned items
  - `POST /v1/inventory/equip` - Equip item
  - `POST /v1/inventory/unequip` - Unequip item
  
- [ ] **B3.4** Add item unlocking system
  - Unlock items through gameplay (level ups, achievements)
  - Random drops after completing runs
  - Rarity-based unlock probability
  - Track unlock events
  
- [ ] **B3.5** Create schemas in `app/schemas/inventory.py`
  - `ItemResponse` - Item details with stats
  - `InventoryResponse` - User's items with equipped status
  - `ProfileResponse` - User profile with avatar and items
  - `EquipItemRequest` - Equip item request
  
- [ ] **B3.6** Update `Profile` model
  - Add `display_name` field (if not exists)
  - Add `customization_metadata` JSON field for colors, styles
  - Add indices for profile queries

### Frontend Status ⚠️ NEEDS BACKEND CONNECTION
Basic UI exists:

**Existing Components:**
- ✅ `CharacterCustomization.js` with cycling equipment
- ✅ Equipment preview display
- ✅ Basic slot management (helmet, armor, weapon, shield)

**Frontend Tasks:**
- [ ] **F3.1** Update `CharacterCustomization.js` with real data
  - Replace hardcoded items with API data
  - Show only unlocked/owned items
  - Display item stats and rarity
  - Add item thumbnails/icons
  
- [ ] **F3.2** Create `CustomizationService.js` in `src/services/`
  - `getProfile()` - Get user profile
  - `getInventory()` - Get owned items
  - `equipItem(itemId, slot)` - Equip item
  - `unequipItem(slot)` - Unequip item
  - `updateAvatar(avatarData)` - Update avatar customization
  
- [ ] **F3.3** Add character preview/avatar system
  - Render character with equipped items
  - Layer system for equipment visualization
  - Use actual item graphics (create asset pipeline)
  - Support different poses/animations
  
- [ ] **F3.4** Create item inventory view
  - Grid/list view of all owned items
  - Filter by slot, rarity
  - Show item details on tap
  - Indicate currently equipped items
  
- [ ] **F3.5** Add item unlock notifications
  - Show modal when new item is unlocked
  - Display item rarity with effects
  - "Equip Now" or "View Inventory" options
  
- [ ] **F3.6** Integrate with MainMenu
  - Show character preview on main menu
  - "Customize" button to open customization screen
  - Display character level and XP bar
  
- [ ] **F3.7** Add color/style customization
  - Color pickers for equipment
  - Preset color schemes
  - Save custom color combinations

**Integration Tasks:**
- [ ] **I3.1** Create/source character and equipment artwork
- [ ] **I3.2** Test item equipping and persistence
- [ ] **I3.3** Verify unlock system works after runs
- [ ] **I3.4** Test avatar rendering performance
- [ ] **I3.5** Add loading states for avatar preview

---

## 🗂️ Shared/Cross-Cutting Tasks

### API & Services
- [ ] **S1** Review and update `src/services/api.js`
  - Add request/response logging
  - Improve error handling
  - Add retry logic for failed requests
  
- [ ] **S2** Create shared types/interfaces (optional TypeScript conversion)
  
- [ ] **S3** Add proper loading states across all screens
  
- [ ] **S4** Implement offline support
  - Cache leaderboard data
  - Queue run submissions if offline
  - Sync when connection restored

### Testing
- [ ] **T1** Write backend unit tests for new services
  - `RunService` tests
  - `LeaderboardService` tests
  - `ProfileService` tests
  
- [ ] **T2** Write integration tests for new endpoints
  
- [ ] **T3** Test anti-cheat system with various attack scenarios
  
- [ ] **T4** Frontend E2E tests with Detox (optional)

### Documentation
- [ ] **D1** Update API documentation with new endpoints
  
- [ ] **D2** Create user guide for new features
  
- [ ] **D3** Add code comments for complex logic
  
- [ ] **D4** Update README files

### DevOps
- [ ] **O1** Set up Redis in production environment
  
- [ ] **O2** Configure Celery workers for background jobs
  
- [ ] **O3** Add monitoring for leaderboard performance
  
- [ ] **O4** Database migrations for any schema changes

---

## 📅 Implementation Order (Recommended)

### Phase 1: Core Gameplay (Days 1-3)
**Goal:** Get dungeon runs fully functional

1. **B1.1** Review RunService
2. **F1.2** Create RunService.js (frontend)
3. **F1.1** Create RunGameplay screen
4. **F1.4** Update dungeon screens to start runs
5. **I1.1** Wire up gameplay flow
6. **I1.2** Test complete run cycle
7. **F1.5** Create RunResultsScreen
8. **F1.6** Add run state management
9. **F1.7** Implement client-side anti-cheat

### Phase 2: Leaderboard (Days 4-5)
**Goal:** Show rankings and competition

1. **B2.1** Create LeaderboardService
2. **B2.4** Create leaderboard schemas
3. **B2.2** Create leaderboard endpoints
4. **F2.2** Create LeaderboardService.js (frontend)
5. **F2.1** Update Leaderboard.js with API
6. **F2.4** Add filters and tabs
7. **B2.3** Implement Redis caching
8. **F2.6** Connect to run results
9. **I2.1-I2.4** Integration testing

### Phase 3: Character System (Days 6-8)
**Goal:** Personalization and progression

1. **B3.1** Create item seed data
2. **B3.2** Create ProfileService
3. **B3.5** Create inventory schemas
4. **B3.3** Create profile endpoints
5. **F3.2** Create CustomizationService.js
6. **F3.1** Update CharacterCustomization.js
7. **F3.4** Create item inventory view
8. **B3.4** Add item unlocking system
9. **F3.3** Add character preview
10. **F3.6** Integrate with MainMenu
11. **I3.1-I3.5** Integration and testing

### Phase 4: Polish & Testing (Days 9-10)
**Goal:** Bug fixes, optimization, UX improvements

1. Complete all **S** (Shared) tasks
2. Complete all **T** (Testing) tasks
3. Complete all **I** (Integration) tasks
4. Performance optimization
5. UI/UX polish
6. Documentation updates

---

## 🎯 Definition of Done

### Per Feature
- [ ] All tasks marked complete
- [ ] Backend endpoints tested and documented
- [ ] Frontend screens functional and polished
- [ ] Integration tests passing
- [ ] No critical bugs
- [ ] Code reviewed
- [ ] User testing completed

### Sprint Complete
- [ ] All three features meet DoD
- [ ] App builds successfully on iOS and Android
- [ ] Backend deployed to staging/production
- [ ] Documentation updated
- [ ] Demo prepared for stakeholders

---

## 📝 Technical Notes

### Backend Architecture Decisions
- **Anti-Cheat:** HMAC-based turn verification prevents score manipulation
- **Leaderboards:** Redis sorted sets for real-time rankings, PostgreSQL for persistence
- **Items:** JSON-based avatar layers for flexibility in customization

### Frontend Architecture Decisions
- **State Management:** Consider React Context or Redux for run state
- **Offline Support:** AsyncStorage for caching and queuing
- **Avatar Rendering:** Layered image system or SVG-based rendering

### Performance Considerations
- Leaderboard queries optimized with indices
- Redis caching for frequently accessed leaderboards
- Paginated API responses to reduce payload size
- Image optimization for character assets

### Security Considerations
- Anti-cheat tokens validated on every submission
- Rate limiting on leaderboard endpoints
- User data isolated by user_id in queries
- Input validation on all customization data

---

## 🐛 Known Issues & Risks

### Current Issues
- [ ] Run abandonment logic incomplete (partially implemented)
- [ ] No character artwork yet (need to create/source)
- [ ] Leaderboard Redis integration not yet implemented
- [ ] No offline queue for run submissions

### Risks
- **High:** Anti-cheat system may have edge cases we haven't tested
- **Medium:** Character customization artwork may take longer than expected
- **Medium:** Redis leaderboard performance at scale unknown
- **Low:** Cross-platform UI consistency for customization screen

---

## 🔄 Sprint Ceremonies

### Daily Standups
- What did you complete yesterday?
- What will you work on today?
- Any blockers?
- Update task checkboxes in this document

### Mid-Sprint Check (Day 5)
- Review Phase 1 & 2 completion
- Adjust timeline if needed
- Address any major blockers

### Sprint Review (End of Sprint)
- Demo all three features
- Gather feedback
- Identify what went well and what to improve

---

## 📚 Additional Resources

### Backend Files to Reference
- `lorebound-backend/app/domain/models.py` - Database models
- `lorebound-backend/app/repositories/` - Data access layer
- `lorebound-backend/app/services/` - Business logic
- `lorebound-backend/app/api/v1/routers/` - API endpoints
- `lorebound-backend/app/schemas/` - Request/response schemas

### Frontend Files to Reference
- `lorebound/src/screens/` - All screen components
- `lorebound/src/services/` - API services
- `lorebound/src/config/config.js` - API configuration
- `lorebound/CharacterCustomization.js` - Customization UI
- `lorebound/Leaderboard.js` - Leaderboard UI

### Useful Backend Commands
```bash
# Start backend with Docker
cd lorebound-backend
docker-compose up

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_content_data.py
python scripts/seed_items_data.py  # Create this

# Test endpoints
python scripts/test_api_endpoints.py
```

### Useful Frontend Commands
```bash
# Start development
cd lorebound
npm start
npm run android
npm run ios

# Clear cache
npm start -- --reset-cache

# View logs
npx react-native log-android
npx react-native log-ios
```

---

## ✅ Completion Checklist

Mark this section when the sprint is complete:

- [ ] All dungeon runs features implemented and tested
- [ ] All leaderboard features implemented and tested
- [ ] All character customization features implemented and tested
- [ ] Backend deployed and stable
- [ ] Frontend builds successfully
- [ ] User testing completed with positive feedback
- [ ] Documentation complete
- [ ] Sprint retrospective held
- [ ] Next sprint planned

---

**Remember:** Update this document as you progress. Check off completed tasks and add notes about implementation decisions or issues encountered. This document is your source of truth for the sprint!

**Last Updated:** October 26, 2025
**Sprint Start Date:** October 26, 2025
**Target Completion:** November 5, 2025 (10 days)

