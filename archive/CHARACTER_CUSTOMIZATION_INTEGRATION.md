# Character Customization Backend Integration

## Overview

The character customization feature has been successfully connected to the backend API. Characters can now be customized and the data is synced between the mobile app and the server.

## What Was Implemented

### Backend Changes

#### 1. Profile Service (`lorebound-backend/app/services/profile_service.py`)
- Created a new `ProfileService` class to handle profile operations
- Methods:
  - `get_user_profile()`: Retrieve user profile
  - `update_user_profile()`: Update profile handle and avatar_layers
  - `update_character_customization()`: Convenience method for character customization
  - `get_profile_with_inventory()`: Get profile with inventory summary

#### 2. Exception Handling (`lorebound-backend/app/services/exceptions.py`)
- Added new exceptions:
  - `ProfileError`: Base exception for profile errors
  - `ProfileNotFoundError`: When profile doesn't exist
  - `HandleAlreadyExistsError`: When handle is already taken

#### 3. Service Dependencies (`lorebound-backend/app/services/dependencies.py`)
- Added `get_profile_service_with_session()` dependency injection
- Integrated ProfileService into the service layer

#### 4. Profile API Endpoints (`lorebound-backend/app/api/v1/routers/profile.py`)
- **GET `/v1/profile/`**: Get current user's profile
  - Returns: handle, level, xp, avatar_layers (character customization)
  - Requires: JWT authentication
  
- **PUT `/v1/profile/`**: Update current user's profile
  - Body: `{ handle?: string, avatar_layers?: object }`
  - Returns: Updated profile
  - Requires: JWT authentication

#### 5. Database Schema (Already Existed)
- `Profile` model has `avatar_layers` JSON field
- Perfect for storing character customization data
- Linked to User via one-to-one relationship

### Frontend Changes

#### 1. Profile Service (`lorebound/src/services/ProfileService.js`)
- Created new service for profile API calls
- Methods:
  - `getProfile()`: Fetch user profile from backend
  - `updateProfile()`: Update profile data
  - `updateCharacterCustomization()`: Update avatar_layers
  - `saveCharacterEquipment()`: Save equipment and color data
  - `loadCharacterCustomization()`: Load character data from backend

#### 2. Character Customization Component (`lorebound/src/screens/CharacterCustomization.js`)
- Enhanced to sync with backend:
  - **Load**: Tries backend first, falls back to AsyncStorage
  - **Save**: Saves to both backend AND AsyncStorage (local backup)
  - **Loading states**: Shows spinner while loading data
  - **Error handling**: Graceful fallback if backend is unavailable
  - **Offline support**: Maintains local copy for offline access

#### 3. Service Export (`lorebound/src/services/index.js`)
- Added ProfileService to exports

## Data Flow

### Loading Character Data
```
1. Component mounts
2. Try to load from backend (ProfileService.loadCharacterCustomization)
3. If successful:
   - Use backend data
   - Save to AsyncStorage for offline access
4. If fails:
   - Fall back to AsyncStorage
   - User sees their last saved local data
```

### Saving Character Data
```
1. User clicks "Save Equipment"
2. Save to AsyncStorage (immediate local backup)
3. Save to backend (ProfileService.saveCharacterEquipment)
4. If backend succeeds:
   - Show "Saved to cloud" message
5. If backend fails:
   - Show "Partially saved" message
   - Data will sync when connection restored
```

## Data Structure

### Frontend Format (AsyncStorage & Component State)
```javascript
{
  equipment: {
    helmet: "Iron Helm",
    armor: "Chainmail",
    weapon: "Battle Axe",
    shield: "Iron Shield"
  },
  colorIndex: 1  // 0=Red, 1=Green, 2=Blue
}
```

### Backend Format (Profile.avatar_layers)
```json
{
  "equipment": {
    "helmet": "Iron Helm",
    "armor": "Chainmail",
    "weapon": "Battle Axe",
    "shield": "Iron Shield"
  },
  "colorIndex": 1,
  "lastUpdated": "2025-11-09T10:30:00Z"
}
```

## API Endpoints

### Get Profile
```http
GET /v1/profile/
Authorization: Bearer <access_token>

Response:
{
  "user_id": "uuid",
  "handle": "PlayerName",
  "level": 15,
  "xp": 12500,
  "avatar_layers": {
    "equipment": {...},
    "colorIndex": 1
  }
}
```

### Update Profile
```http
PUT /v1/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "avatar_layers": {
    "equipment": {
      "helmet": "Iron Helm",
      "armor": "Chainmail",
      "weapon": "Battle Axe",
      "shield": "Iron Shield"
    },
    "colorIndex": 1
  }
}

Response: <Updated profile object>
```

## Testing the Integration

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. Mobile app running on emulator/device
3. User must be logged in

### Test Steps

1. **Test Load from Backend**
   ```
   - Open app and log in
   - Navigate to Character Customization
   - Should see loading spinner
   - Should load character data from backend
   ```

2. **Test Customization**
   ```
   - Change equipment (helmet, armor, weapon, shield)
   - Change knight color
   - Click "Save Equipment"
   - Should see "Saved to cloud" message
   ```

3. **Test Backend Persistence**
   ```
   - Save customization
   - Close app completely
   - Reopen app and navigate to Character Customization
   - Should load the same customization from backend
   ```

4. **Test Offline Mode**
   ```
   - Turn off internet/backend
   - Open Character Customization
   - Should load from AsyncStorage (local data)
   - Make changes and save
   - Should see "Partially saved" message
   - Turn internet back on
   - Save again - should sync to backend
   ```

5. **Test Cross-Device Sync**
   ```
   - Save customization on Device A
   - Log in on Device B with same account
   - Open Character Customization
   - Should see same customization as Device A
   ```

### Debugging

**Check Backend Logs:**
```bash
cd lorebound-backend
docker-compose logs -f api
```

**Check Frontend Logs:**
```bash
# Android
npx react-native log-android

# iOS
npx react-native log-ios
```

**Check API in Browser:**
- Swagger UI: http://localhost:8000/docs
- Test endpoints directly from Swagger

### Common Issues

1. **"Profile not found" error**
   - User profile wasn't created during registration
   - Check that AuthService creates profile for new users

2. **"Failed to update profile" error**
   - JWT token expired - app should auto-refresh
   - Check network connection
   - Verify backend is running

3. **Data not loading from backend**
   - Check console logs for API errors
   - Verify user is authenticated
   - Check backend endpoint is accessible

## Future Enhancements

1. **Inventory Integration**
   - Connect to actual Item and Inventory models
   - Let users equip items they've earned
   - Show item stats and rarity

2. **Character Preview**
   - Render character with actual equipment sprites
   - Show equipment stats bonus

3. **Sync Indicator**
   - Show sync status (synced/pending/offline)
   - Auto-sync when connection restored

4. **Validation**
   - Validate equipment combinations
   - Ensure user owns items before equipping

## Files Modified/Created

### Backend
- ✅ `lorebound-backend/app/services/profile_service.py` (NEW)
- ✅ `lorebound-backend/app/services/exceptions.py` (UPDATED)
- ✅ `lorebound-backend/app/services/dependencies.py` (UPDATED)
- ✅ `lorebound-backend/app/api/v1/routers/profile.py` (UPDATED)

### Frontend
- ✅ `lorebound/src/services/ProfileService.js` (NEW)
- ✅ `lorebound/src/services/index.js` (UPDATED)
- ✅ `lorebound/src/screens/CharacterCustomization.js` (UPDATED)

### Database
- ✅ Using existing `Profile.avatar_layers` field (no migration needed)

## Architecture Benefits

1. **Separation of Concerns**
   - Repository layer handles database operations
   - Service layer handles business logic
   - API layer handles HTTP requests/responses

2. **Error Handling**
   - Graceful fallback to local storage
   - User-friendly error messages
   - Doesn't break app if backend is down

3. **Offline-First**
   - Data saved locally first
   - Syncs to backend when available
   - Users can customize even offline

4. **Scalability**
   - Easy to add more customization options
   - Can integrate with inventory system
   - Ready for cross-platform sync

## Summary

The character customization feature now has a complete backend integration:
- ✅ Data persists to PostgreSQL database
- ✅ Syncs across devices
- ✅ Works offline with local backup
- ✅ Graceful error handling
- ✅ RESTful API endpoints
- ✅ JWT authentication
- ✅ Service layer architecture

Users can now customize their characters and have confidence that their choices are saved both locally and in the cloud!

