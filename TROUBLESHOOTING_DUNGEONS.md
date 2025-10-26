# Troubleshooting "Failed to load dungeons" Error

## 🔍 Common Causes & Solutions

### Issue: "Failed to load dungeons. Please check your connection and try again"

This error occurs when the DungeonSelect screen can't fetch dungeons from the backend. Here are the most common causes:

---

## ✅ Step 1: Verify Backend is Running

**Check if backend containers are running:**
```powershell
docker ps --filter "name=lorebound-backend"
```

**Expected output:** Should show 4 containers running:
- `lorebound-backend-api-1` (Status: Up)
- `lorebound-backend-db-1` (Status: Up, healthy)
- `lorebound-backend-redis-1` (Status: Up, healthy)
- `lorebound-backend-worker-1` (Status: Up)

**If not running:**
```powershell
cd lorebound-backend
docker-compose up -d
```

---

## ✅ Step 2: Check API Health

```powershell
curl http://localhost:8000/healthz
```

**Expected output:** 
```json
{"status":"healthy","version":"0.1.0",...}
```

**If unhealthy:** Check API logs:
```powershell
docker logs lorebound-backend-api-1 --tail 50
```

---

## ✅ Step 3: Verify Authentication

The dungeons endpoint requires authentication. Make sure you're logged in!

**Test authentication manually:**
```powershell
$body = '{"email":"integrationtest@example.com","password":"TestPass123!"}'
Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method Post -ContentType "application/json" -Body $body
```

**Expected:** Should return tokens

**In the app:**
- Have you logged in or registered?
- Try logging out and logging back in
- Token might have expired (15 min default)

---

## ✅ Step 4: Check Device/Emulator Connection

### Are you using Android Emulator?
The API URL should be `http://10.0.2.2:8000`

**Check config:**
```javascript
// lorebound/src/config/config.js
if (Platform.OS === 'android') {
  return 'http://10.0.2.2:8000';  // ✅ Correct for emulator
}
```

### Are you using iOS Simulator?
The API URL should be `http://localhost:8000`

### Are you using a Physical Device?
You need your computer's local IP address!

**Find your IP:**
```powershell
ipconfig
# Look for "IPv4 Address" under your active network adapter
# Usually something like: 192.168.1.100
```

**Update config:**
```javascript
// lorebound/src/config/config.js
const getApiBaseUrl = () => {
  if (__DEV__) {
    if (Platform.OS === 'android') {
      return 'http://192.168.1.100:8000';  // Use YOUR IP!
    } else {
      return 'http://192.168.1.100:8000';  // Use YOUR IP!
    }
  }
  // ...
};
```

**After changing config:**
```bash
# Stop Metro
# Ctrl+C in Metro terminal

# Clear cache and restart
npm start -- --reset-cache
```

---

## ✅ Step 5: Check Metro Bundler Logs

Look at the terminal where Metro is running for errors:

**Common errors to look for:**
- `Network request failed` - Connection issue
- `403 Forbidden` - Authentication issue
- `404 Not Found` - Wrong API endpoint
- `Timeout` - Backend too slow or not responding

---

## ✅ Step 6: Test API Endpoint Directly

**Test the dungeons endpoint with authentication:**

```powershell
# 1. Login and get token
$loginBody = '{"email":"integrationtest@example.com","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.tokens.access_token

# 2. Test dungeons endpoint
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/v1/content/dungeons" -Headers $headers
```

**Expected output:** Array of 4 dungeons

**If this works but app doesn't:**
- Issue is in the frontend
- Check if token is being stored/retrieved correctly
- Check ContentService code

**If this fails:**
- Issue is in the backend
- Check backend logs
- Verify dungeons are seeded

---

## ✅ Step 7: Verify Dungeons Are Seeded

```powershell
docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM dungeons;"
```

**Expected:** Should show `4` dungeons

**If 0 dungeons:**
```powershell
docker exec lorebound-backend-api-1 poetry run python scripts/seed_content_data.py
```

---

## ✅ Step 8: Check AsyncStorage (Authentication State)

The app stores the auth token in AsyncStorage. If it's corrupted or expired, you'll get authentication errors.

**Solution: Clear app data and login again**

**Android:**
```
Settings → Apps → LoreBound → Storage → Clear Data
```

**iOS:**
```
Uninstall and reinstall the app
```

**Or in the app:**
- Go to settings/profile (if you have it)
- Tap "Logout"
- Login again

---

## 🔧 Quick Fix Checklist

Run through these in order:

- [ ] Backend running? (`docker ps`)
- [ ] API healthy? (`curl http://localhost:8000/healthz`)
- [ ] Logged into app? (Try logout/login)
- [ ] Using correct IP for your device type?
  - [ ] Android Emulator: `10.0.2.2:8000` ✅
  - [ ] iOS Simulator: `localhost:8000` ✅
  - [ ] Physical Device: `192.168.x.x:8000` (your IP)
- [ ] Dungeons seeded? (Check database)
- [ ] Metro bundler running? (No errors in terminal)
- [ ] Cleared cache? (`npm start -- --reset-cache`)

---

## 🐛 Debug Mode

### Enable Detailed Logging in ContentService

Edit `lorebound/src/services/ContentService.js`:

```javascript
async getDungeons() {
  return await AuthUtils.authenticatedRequest(async (token) => {
    try {
      console.log('🔍 Fetching dungeons from:', `${this.baseURL}/v1/content/dungeons`);
      console.log('🔑 Using token:', token.substring(0, 20) + '...');
      
      const response = await this.fetchWithTimeout(
        `${this.baseURL}/v1/content/dungeons`,
        // ... rest of code
      );

      console.log('📡 Response status:', response.status);
      const data = await response.json();
      console.log('📦 Response data:', data);

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch dungeons');
      }

      return data;
    } catch (error) {
      console.error('❌ Get dungeons error:', error);
      console.error('❌ Error details:', {
        message: error.message,
        name: error.name,
        stack: error.stack
      });
      throw error;
    }
  });
}
```

Then check Metro logs for detailed output!

---

## 🎯 Most Common Issue: Not Authenticated

**90% of the time, this error means:**
1. You haven't logged in yet
2. Your token expired (15 minutes)
3. Token not stored correctly

**Quick fix:**
1. Open app
2. Go to auth screen (logout if needed)
3. Login with: `integrationtest@example.com` / `TestPass123!`
4. Navigate to Dungeon Select again

---

## 📱 Platform-Specific Issues

### Android Emulator
**Problem:** Can't connect to `localhost:8000`  
**Solution:** Must use `10.0.2.2:8000` (already in config)

**Problem:** "Network request failed"  
**Solution:** Make sure Windows Firewall isn't blocking port 8000

### iOS Simulator  
**Problem:** Can't connect to backend  
**Solution:** Use `localhost:8000` (already in config)

### Physical Device (Android/iOS)
**Problem:** Can't connect to backend  
**Solution:** 
1. Device must be on same WiFi as computer
2. Use computer's local IP (not localhost)
3. Update `config.js` with your IP

---

## 🚑 Emergency Reset

If nothing works, try a full reset:

```powershell
# 1. Stop everything
docker-compose down

# 2. Clear app data (uninstall/reinstall or clear storage)

# 3. Restart backend
cd lorebound-backend
docker-compose up -d

# 4. Wait for healthy status
Start-Sleep -Seconds 10

# 5. Verify dungeons
docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT COUNT(*) FROM dungeons;"

# 6. Re-seed if needed
docker exec lorebound-backend-api-1 poetry run python scripts/seed_content_data.py

# 7. Restart Metro with cache clear
cd ../lorebound
npm start -- --reset-cache

# 8. Rebuild app
npm run android  # or npm run ios
```

---

## ✅ Success Indicators

When everything is working correctly, you should see:

**Backend:**
- ✅ 4 containers running and healthy
- ✅ API responds to health check
- ✅ 4 dungeons in database
- ✅ Auth endpoints work

**Frontend:**
- ✅ Can login/register successfully
- ✅ DungeonSelect shows loading spinner
- ✅ 4 dungeons appear with icons and titles
- ✅ Tapping dungeon navigates to gameplay
- ✅ No errors in Metro terminal

---

## 📝 Still Not Working?

**Check these files:**
1. `lorebound/src/config/config.js` - API URL correct?
2. `lorebound/src/services/ContentService.js` - No syntax errors?
3. `lorebound/src/services/authUtils.js` - Token management working?
4. `lorebound/src/screens/DungeonSelect.js` - Error handling correct?

**Get help:**
1. Copy Metro bundler errors
2. Copy backend logs: `docker logs lorebound-backend-api-1 --tail 100`
3. Share error details

---

## 🎉 Once It Works

You should see:
- 🏛️ Ancient History Depths
- ⚽ Sports Arena Challenge
- 🎵 Musical Harmony Tower
- 📺 Pop Culture Arcade

All ready to play! 🎮

