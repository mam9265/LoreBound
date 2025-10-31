# 📱 Frontend Testing Checklist

Quick reference checklist for testing Phase 1 & 2 frontend functionality.

## 🚀 Getting Started

### Prerequisites
- [ ] Backend is running (`docker-compose up -d`)
- [ ] Backend tests passed (`.\test_integration.ps1`)
- [ ] Node.js installed
- [ ] Android Studio or Xcode installed
- [ ] Emulator/Simulator or physical device ready

### Launch App
```bash
# Quick start
.\start_frontend_test.ps1

# OR Manual start
cd lorebound
npm install
npm start                    # Terminal 1
npm run android              # Terminal 2 (or npm run ios)
```

### Login Credentials
```
Email: integrationtest@example.com
Password: TestPass123!
```

---

## ✅ Phase 1: Dungeon Runs Testing

### Main Menu
- [ ] App loads without crashes
- [ ] Main menu displays correctly
- [ ] All navigation buttons visible
- [ ] Can navigate to different screens

### Dungeon Selection
- [ ] See 4 dungeons:
  - [ ] Ancient History Depths
  - [ ] Sports Arena Challenge
  - [ ] Musical Harmony Tower
  - [ ] Pop Culture Arcade
- [ ] Each dungeon shows title and category
- [ ] "Start" or "Play" button works

### Starting a Run
- [ ] Can tap dungeon to start
- [ ] Loading indicator appears (if applicable)
- [ ] Transitions to gameplay screen
- [ ] No errors or crashes

### Gameplay
- [ ] Questions display correctly
- [ ] Timer starts (if implemented)
- [ ] Can read questions clearly
- [ ] Answer choices are visible
- [ ] Can tap/select an answer
- [ ] Visual feedback on selection
- [ ] Next question appears
- [ ] Score updates (if visible)
- [ ] Lives/health bar works (if implemented)
- [ ] Progress indicator shows (e.g., "Question 3/10")

### Completing Run
- [ ] Can answer all questions
- [ ] Smooth transitions between questions
- [ ] No crashes during run
- [ ] Transitions to results screen
- [ ] Results screen loads properly

### Results Screen
- [ ] Final score displayed
- [ ] Correct/incorrect count shown
- [ ] Time taken displayed (if applicable)
- [ ] Statistics are accurate
- [ ] "Play Again" button works
- [ ] "View History" button works
- [ ] Can navigate back to menu

### Run History
- [ ] History screen loads
- [ ] Completed runs appear in list
- [ ] Each run shows:
  - [ ] Dungeon name
  - [ ] Score
  - [ ] Date/time
- [ ] Runs ordered by recency
- [ ] Pull-to-refresh works
- [ ] Can scroll through history
- [ ] Tapping run shows details (if implemented)

---

## 🏆 Phase 2: Leaderboard Testing

### Access Leaderboard
- [ ] Can navigate to leaderboard from menu
- [ ] Leaderboard screen loads
- [ ] No errors or blank screens
- [ ] Loading indicator appears (if applicable)

### Leaderboard Display
- [ ] Player ranks visible (1, 2, 3, ...)
- [ ] Player names/handles displayed
- [ ] Scores shown next to names
- [ ] Your entry highlighted differently
- [ ] Total participants count (if shown)

### Scope Tabs
- [ ] Three tabs visible:
  - [ ] "Today"
  - [ ] "This Week" or "Weekly"
  - [ ] "All-Time"
- [ ] Active tab is highlighted
- [ ] Can tap each tab

### Today's Leaderboard
- [ ] Tap "Today" tab
- [ ] Data loads/updates
- [ ] Shows today's date
- [ ] Rankings for today only
- [ ] Your runs from today appear (if any)

### Weekly Leaderboard
- [ ] Tap "Weekly" tab
- [ ] Data loads/updates
- [ ] Shows current week (e.g., "Week 43")
- [ ] Rankings for this week
- [ ] Your runs from this week appear

### All-Time Leaderboard
- [ ] Tap "All-Time" tab
- [ ] Data loads/updates
- [ ] Shows overall rankings
- [ ] All your completed runs counted
- [ ] Cumulative scores displayed

### Refresh Functionality
- [ ] Pull down to refresh
- [ ] Refresh indicator animates
- [ ] Data reloads from server
- [ ] Indicator disappears after load

### Your Rank
- [ ] Can find yourself in leaderboard
- [ ] Your entry is highlighted
- [ ] "Your Rank" section shows (if implemented):
  - [ ] Your current rank
  - [ ] Your score
  - [ ] Players above you
  - [ ] Players below you

### Statistics (if implemented)
- [ ] Total participants shown
- [ ] Average score displayed
- [ ] Highest score shown
- [ ] Your percentile (optional)
- [ ] Stats update per scope

---

## 🔄 Integration Testing

### Complete Flow Test
1. [ ] Note current All-Time rank and score
2. [ ] Start a new dungeon run
3. [ ] Answer questions (try for high score!)
4. [ ] Complete the run
5. [ ] View results - note final score
6. [ ] Navigate to Run History
7. [ ] Verify new run appears in history
8. [ ] Navigate to Leaderboard
9. [ ] Pull to refresh leaderboard
10. [ ] Verify in "Today" scope:
    - [ ] Your new run is counted
    - [ ] Rank updated (if applicable)
11. [ ] Verify in "Weekly" scope:
    - [ ] Your new run is counted
12. [ ] Verify in "All-Time" scope:
    - [ ] Total score increased
    - [ ] Rank may have changed

### Multiple Runs Test
1. [ ] Complete 2-3 runs with different scores
2. [ ] After each run:
   - [ ] Check Run History updates
   - [ ] Check Leaderboard updates
   - [ ] Verify stats are accurate
3. [ ] Try different dungeons
4. [ ] Verify all runs tracked correctly

---

## 🐛 Bug Tracking

### If You Find Issues, Note:

**Issue #____**
- **Screen:** [Where it happened]
- **Steps:** [What you did]
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Error:** [Any error messages]
- **Device:** [Android/iOS, emulator/physical]

---

## 📊 Performance Check

- [ ] App launches quickly (< 5 seconds)
- [ ] Screens transition smoothly
- [ ] No lag when scrolling
- [ ] Questions load fast
- [ ] Leaderboard loads in < 2 seconds
- [ ] Pull-to-refresh is responsive
- [ ] No memory leaks (app doesn't slow down over time)
- [ ] No crashes during testing session

---

## 🎯 Final Verification

### Must Work:
- [x] Backend is running and healthy
- [ ] Can register/login successfully
- [ ] Can complete a full dungeon run
- [ ] Results are accurate
- [ ] Run history displays correctly
- [ ] Leaderboard shows all 3 scopes
- [ ] Leaderboard updates after runs
- [ ] App doesn't crash

### Nice to Have Working:
- [ ] Smooth animations
- [ ] Sound effects (if implemented)
- [ ] Haptic feedback (if implemented)
- [ ] Offline mode handling
- [ ] Error messages are user-friendly
- [ ] Loading states are clear

---

## ✅ Sign-Off

**Tester:** _______________  
**Date:** _______________  
**Device/Emulator:** _______________  
**Overall Result:** ⬜ PASS  ⬜ FAIL  ⬜ NEEDS WORK

**Notes:**
```
[Add any additional notes, observations, or suggestions here]
```

---

## 🆘 Quick Troubleshooting

**App won't build:**
```bash
cd lorebound
npm start -- --reset-cache
```

**Backend connection issues:**
- Check `src/config/config.js` has correct IP
- Android emulator uses `10.0.2.2:8000`
- iOS simulator uses `localhost:8000`

**403 Forbidden errors:**
- Log out and log back in
- Token may have expired

**Questions won't load:**
- Check backend has questions seeded
- Verify `floor` parameter is sent

**Need help?**
- Check Metro Bundler output for JS errors
- Check backend logs: `docker logs lorebound-backend-api-1`
- See `FRONTEND_TEST_GUIDE.md` for detailed troubleshooting

