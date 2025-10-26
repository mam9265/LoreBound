# Frontend Testing Guide - Phase 1 & 2

## 🎯 Objective

Test the React Native frontend to ensure:
- It connects to the backend successfully
- Phase 1 (Dungeon Runs) screens work properly
- Phase 2 (Leaderboard) screen displays correctly
- All user interactions function as expected

---

## 📋 Pre-Test Checklist

### Backend Must Be Running ✅
- [x] Docker services are up (from previous test)
- [x] API is accessible at `http://localhost:8000`
- [x] Database has dungeons and questions seeded

### Frontend Requirements
- [ ] Node.js installed (check: `node --version`)
- [ ] React Native environment set up
- [ ] Android Studio (for Android) or Xcode (for iOS)
- [ ] Physical device or emulator/simulator ready

---

## 🚀 Step-by-Step Frontend Testing

### Step 1: Install Dependencies

```bash
cd lorebound
npm install
```

**Expected Output:** Dependencies install without errors

### Step 2: Check Configuration

The API configuration should already be correct in `src/config/config.js`:
- **Android Emulator:** Uses `http://10.0.2.2:8000`
- **iOS Simulator:** Uses `http://localhost:8000`
- **Physical Device:** You'll need to update to your computer's IP

To find your IP (if using physical device):

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" (usually 192.168.x.x)
```

**Mac/Linux:**
```bash
ifconfig | grep "inet "
```

If you need to update for physical device, edit `lorebound/src/config/config.js` and change the return value in the development section.

### Step 3: Start Metro Bundler

Open a terminal in the `lorebound` directory:

```bash
npm start
```

**Expected Output:**
```
                ######                ######
              ###     ####        ####     ###
            ##          ###    ###          ##
            ##             ####             ##
            ##             ####             ##
            ##           ##    ##           ##
            ##         ###      ###         ##
              ###     ####        ####     ###
                ######                ######

               Welcome to Metro v0.80.x
```

**Keep this terminal running!** It's the JavaScript bundler.

### Step 4: Launch the App

**Option A: Android Emulator**

Open a **new terminal** in `lorebound`:

```bash
npm run android
```

**Option B: iOS Simulator (Mac only)**

```bash
npm run ios
```

**Expected:** App should build and launch on your device/simulator

### Step 5: Initial App Launch

When the app first launches:

1. **If you see AuthScreen:**
   - You need to register or login
   - Use the test account we created: `integrationtest@example.com` / `TestPass123!`
   - Or create a new account

2. **If you see MainMenu:**
   - You're already logged in
   - Great! Continue to testing

---

## 🧪 Testing Phase 1: Dungeon Runs

### Test 1: Main Menu Navigation

**Location:** Main Menu Screen

**Test Steps:**
1. Verify you see the main menu with options:
   - [ ] "Select Dungeon" or similar button
   - [ ] "View History" or similar button
   - [ ] "Leaderboard" button (if visible)

2. Check that all buttons are clickable

**Expected Result:** All navigation options are visible and responsive

---

### Test 2: Dungeon Selection

**Location:** Dungeon Select Screen

**Test Steps:**
1. Tap "Select Dungeon" or navigate to dungeon selection
2. Verify dungeons appear:
   - [ ] Ancient History Depths (History)
   - [ ] Sports Arena Challenge (Sports)
   - [ ] Musical Harmony Tower (Music)
   - [ ] Pop Culture Arcade (Pop Culture)

3. Check each dungeon card shows:
   - [ ] Title
   - [ ] Category/Description
   - [ ] "Start" or "Play" button

**Expected Result:** 4 dungeons display with proper information

**Screenshot Opportunity:** Dungeon selection screen

---

### Test 3: Starting a Run

**Location:** Dungeon Select → RunGameplay

**Test Steps:**
1. Select any dungeon (e.g., "Ancient History Depths")
2. Tap "Start" or "Play"
3. Verify the run starts:
   - [ ] Questions appear
   - [ ] Timer starts (if applicable)
   - [ ] Answer choices are visible and clickable
   - [ ] Score/lives display (if applicable)

**Expected Result:** Run begins smoothly with questions loaded

**Common Issues:**
- If questions don't load: Check backend logs for errors
- If 403 error: Token may have expired, try logging out and back in
- If blank screen: Check Metro bundler for JavaScript errors

---

### Test 4: Answering Questions

**Location:** RunGameplay Screen

**Test Steps:**
1. Read the first question
2. Tap an answer choice
3. Verify:
   - [ ] Answer is registered (visual feedback)
   - [ ] Next question appears automatically or with a button
   - [ ] Score updates (if visible)
   - [ ] Progress indicator updates

4. Answer at least 3-5 questions
5. Try getting some right and some wrong (if you know the answers!)

**Expected Result:** 
- Smooth question progression
- Clear feedback on answers
- No crashes or freezes

**Test Questions to Try:**
- "Which ancient civilization built the pyramids of Giza?" → **Egyptians**
- "In which sport would you perform a slam dunk?" → **Basketball**
- "How many strings does a standard guitar have?" → **6**

---

### Test 5: Completing a Run

**Location:** RunGameplay → RunResults

**Test Steps:**
1. Answer all questions in the run (or run out of lives)
2. Verify run completion:
   - [ ] Transition to results screen
   - [ ] No errors or crashes

3. On RunResults screen, check for:
   - [ ] Final score displayed
   - [ ] Number of correct/incorrect answers
   - [ ] Completion time (if applicable)
   - [ ] Statistics or breakdown
   - [ ] "Play Again" button
   - [ ] "View History" or "Back to Menu" button

**Expected Result:** Results screen shows accurate statistics

**Screenshot Opportunity:** Results screen with your score

---

### Test 6: Run History

**Location:** Main Menu → RunHistory

**Test Steps:**
1. Navigate to Run History (from menu or results screen)
2. Verify history displays:
   - [ ] List of completed runs appears
   - [ ] Each run shows: dungeon name, score, date/time
   - [ ] Runs are ordered (most recent first)

3. Test pull-to-refresh:
   - [ ] Pull down on the list
   - [ ] Refresh indicator appears
   - [ ] List reloads

4. Try tapping a run (if detail view exists):
   - [ ] Run details appear
   - [ ] Question-by-question breakdown (if implemented)

**Expected Result:** All completed runs appear in history

**Common Issues:**
- If history is empty: Make sure you completed at least one run
- If old runs don't appear: Check API endpoint `/v1/runs/` response

---

### Test 7: Play Multiple Runs

**Location:** Multiple screens

**Test Steps:**
1. Complete 2-3 runs across different dungeons
2. Vary your scores (try to get different scores each time)
3. After each run, verify:
   - [ ] Run is saved
   - [ ] History updates with new run
   - [ ] Stats update correctly

**Expected Result:** Multiple runs tracked accurately

---

## 🏆 Testing Phase 2: Leaderboard

### Test 8: Access Leaderboard

**Location:** Main Menu → Leaderboard

**Test Steps:**
1. From main menu, tap "Leaderboard" button
2. Verify leaderboard screen loads:
   - [ ] No errors or crashes
   - [ ] Loading indicator appears (if applicable)
   - [ ] Screen displays without blank areas

**Expected Result:** Leaderboard screen loads successfully

---

### Test 9: View Leaderboard Scopes

**Location:** Leaderboard Screen

**Test Steps:**
1. Check for scope tabs/buttons:
   - [ ] "Today" tab
   - [ ] "This Week" or "Weekly" tab
   - [ ] "All-Time" tab

2. Verify current active scope is highlighted

3. Check leaderboard displays:
   - [ ] Player ranks (1, 2, 3, etc.)
   - [ ] Player handles/names
   - [ ] Scores
   - [ ] Total participants count (optional)

**Expected Result:** Default scope (probably All-Time) shows data

**Note:** If you're the only player, you should see your rank and score!

---

### Test 10: Switch Between Scopes

**Location:** Leaderboard Screen

**Test Steps:**
1. Tap "Today" tab
   - [ ] Loading indicator appears (if applicable)
   - [ ] Data updates to today's rankings
   - [ ] Tab is highlighted as active

2. Tap "This Week" tab
   - [ ] Data updates to weekly rankings
   - [ ] Week period displayed (e.g., "Week 43, 2025")

3. Tap "All-Time" tab
   - [ ] Data updates to all-time rankings

4. Verify for each scope:
   - [ ] Rankings may be different
   - [ ] Scores are appropriate for the time period
   - [ ] Your rank appears (if you've completed runs)

**Expected Result:** Smooth transitions between scopes with correct data

**Common Issues:**
- If 403 errors occur: Check trailing slashes in API URLs (`/v1/leaderboards/`)
- If data doesn't change: Check API responses in Chrome DevTools or React Native Debugger

---

### Test 11: Pull-to-Refresh Leaderboard

**Location:** Leaderboard Screen

**Test Steps:**
1. On any leaderboard scope, pull down to refresh
2. Verify:
   - [ ] Refresh indicator appears
   - [ ] API request is made (check backend logs if needed)
   - [ ] Data reloads
   - [ ] Indicator disappears

3. Complete a new run with a high score
4. Return to leaderboard and refresh
5. Check if your rank improved:
   - [ ] New score reflected
   - [ ] Rank updated (if score was high enough)

**Expected Result:** Refresh updates leaderboard data

---

### Test 12: User Rank Display

**Location:** Leaderboard Screen

**Test Steps:**
1. Look for your own entry in the leaderboard
2. Verify it's highlighted or marked differently
3. Check if there's a "Your Rank" section showing:
   - [ ] Your current rank
   - [ ] Your score
   - [ ] Players near you (neighbors)

**Expected Result:** Your rank is easy to identify

---

### Test 13: Leaderboard Stats (if implemented)

**Location:** Leaderboard Screen

**Test Steps:**
1. Look for stats section showing:
   - [ ] Total participants
   - [ ] Average score
   - [ ] Highest score
   - [ ] Your percentile (optional)

2. Verify stats make sense:
   - [ ] Numbers are reasonable
   - [ ] Stats update when scope changes

**Expected Result:** Stats display accurately

---

## 🔄 Complete Integration Flow Test

### Test 14: End-to-End Flow

**Complete Flow:** Login → Play Run → See Updated Leaderboard

**Test Steps:**
1. **Start Fresh:**
   - Note your current rank on All-Time leaderboard
   - Note your total score

2. **Play a Run:**
   - Select a dungeon
   - Answer questions (try to get high score!)
   - Complete the run
   - Note your final score

3. **Check Results:**
   - Verify score on results screen
   - Navigate to Run History
   - Confirm run appears in history

4. **Check Leaderboard:**
   - Navigate to Leaderboard
   - Pull to refresh (important!)
   - Verify:
     - [ ] Your total score increased
     - [ ] Your rank updated (may change)
     - [ ] New run is counted

5. **Check All Scopes:**
   - View "Today" leaderboard → Your run should appear
   - View "This Week" leaderboard → Your run should appear
   - View "All-Time" leaderboard → Your total updated

**Expected Result:** Complete flow works seamlessly, data propagates correctly

---

## 🐛 Common Issues & Solutions

### Issue: App Won't Build

**Symptoms:** Build errors, red screen

**Solutions:**
```bash
# Clear cache and rebuild
cd lorebound
npm start -- --reset-cache

# Clean Android build
cd android
./gradlew clean
cd ..
npm run android

# Clean iOS build (Mac only)
cd ios
pod install
cd ..
npm run ios
```

### Issue: Backend Connection Failed

**Symptoms:** "Network request failed", timeout errors

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/healthz`
2. Check `src/config/config.js` has correct URL
3. For Android emulator: Must use `10.0.2.2` not `localhost`
4. For physical device: Update to your computer's IP address

### Issue: Authentication Errors (403 Forbidden)

**Symptoms:** Can't fetch data, 403 errors

**Solutions:**
1. Log out and log back in
2. Check token is being stored properly
3. Verify `Authorization` header is sent with requests
4. Check token hasn't expired (default 15 minutes)

### Issue: Questions Don't Load (422 Error)

**Symptoms:** Blank screen after starting run

**Solutions:**
1. Verify `floor` parameter is sent: `?dungeon_id={id}&floor=1&count=10`
2. Check `RunService.js` or `api.js` for question fetch logic
3. Ensure dungeon_id is valid UUID

### Issue: Leaderboard Shows 403 Errors

**Symptoms:** Leaderboard won't load

**Solutions:**
1. Check API URLs in `LeaderboardService.js`
2. Ensure trailing slashes: `/v1/leaderboards/` not `/v1/leaderboards`
3. Verify token is valid

### Issue: UI Elements Overlapping or Cut Off

**Symptoms:** Text overflows, buttons hidden

**Solutions:**
1. Check device screen size compatibility
2. Test on different device sizes
3. May need style adjustments for your specific screens

---

## 📸 Testing Checklist Summary

Use this checklist while testing:

### Authentication
- [ ] Can register new account
- [ ] Can login with existing account
- [ ] Token persists between app restarts
- [ ] Can logout successfully

### Phase 1: Dungeon Runs
- [ ] Main menu displays correctly
- [ ] Dungeon selection shows all 4 dungeons
- [ ] Can start a run
- [ ] Questions load and display
- [ ] Can select answers
- [ ] Run completes successfully
- [ ] Results screen shows accurate data
- [ ] Run history displays completed runs
- [ ] Can play multiple runs
- [ ] Stats update correctly

### Phase 2: Leaderboard
- [ ] Leaderboard screen loads
- [ ] All three scopes accessible (Today, Weekly, All-Time)
- [ ] Can switch between scopes
- [ ] Rankings display correctly
- [ ] Your rank is visible
- [ ] Pull-to-refresh works
- [ ] Leaderboard updates after completing runs
- [ ] Stats are accurate

### Integration
- [ ] Complete flow: Login → Play → Leaderboard works
- [ ] Data persists correctly
- [ ] No crashes or major bugs
- [ ] Performance is acceptable

---

## 🎯 Success Criteria

Testing is complete when:

- [ ] ✅ App builds and runs without errors
- [ ] ✅ Can complete a full dungeon run
- [ ] ✅ Run history displays correctly
- [ ] ✅ Leaderboard shows all three scopes
- [ ] ✅ Leaderboard updates after runs
- [ ] ✅ No critical bugs or crashes
- [ ] ✅ User experience is smooth

---

## 📝 Reporting Issues

If you find bugs, note:
1. **What you were doing** (exact steps)
2. **What happened** (the bug)
3. **What you expected** (correct behavior)
4. **Error messages** (from Metro bundler or device)
5. **Device/Simulator** (Android/iOS, version)

Check these for errors:
- **Metro Bundler output** (in terminal where you ran `npm start`)
- **Device logs** (use `npx react-native log-android` or `log-ios`)
- **Backend API logs** (check for 4xx/5xx errors)

---

## 🚀 Next Steps After Testing

Once frontend testing is complete:

1. **Document any UI/UX improvements needed**
2. **Note any backend API adjustments required**
3. **Plan Phase 3 features** (Daily Challenges, etc.)
4. **Consider adding unit tests** for critical components
5. **Prepare for production deployment**

---

**Ready to test? Let's go!** 🎮

Start with Step 1 and work through systematically. The backend is already running and ready for your frontend to connect!

