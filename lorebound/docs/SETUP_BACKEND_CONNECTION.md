# Backend Connection Setup Guide

This guide explains how to connect the LoreBound React Native frontend to the FastAPI backend.

## ✅ What Has Been Done

The frontend login functionality has been connected to the backend with the following changes:

1. **Created `config.js`** - Configuration file for API settings
   - Default development URL: `http://localhost:8000`
   - Configurable for production deployment

2. **Created `api.js`** - API service layer with methods for:
   - User login (`/v1/auth/login`)
   - User registration (`/v1/auth/register`)
   - Token refresh (`/v1/auth/refresh`)
   - Get current user (`/v1/auth/me`)
   - User logout (`/v1/auth/logout`)

3. **Updated `AuthScreen.js`** - Connected UI to backend:
   - Login function now calls the backend API
   - Registration function now calls the backend API
   - Tokens are stored securely in AsyncStorage
   - Loading state with spinner during API calls
   - Proper error handling with user-friendly messages

4. **Updated `Styles.js`** - Added disabled button styling

5. **Updated `package.json`** - Added AsyncStorage dependency

## 🚀 Setup Instructions

### Step 1: Install Dependencies

Navigate to the `lorebound` directory and install the new dependency:

```bash
cd lorebound
npm install
```

### Step 2: Configure API URL

The default configuration in `config.js` uses:
- **Development**: `http://localhost:8000`
- **Production**: You'll need to update this with your production URL

#### For Testing on Different Devices:

**Android Emulator:**
- The emulator can access `localhost` but you may need to use `10.0.2.2` instead
- Update `config.js` if needed:
  ```javascript
  const API_BASE_URL = __DEV__ 
    ? 'http://10.0.2.2:8000'  // Android emulator
    : 'https://your-production-url.com';
  ```

**iOS Simulator:**
- Can use `localhost` directly
- Default configuration should work

**Physical Device:**
- Must use your computer's local IP address
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Update `config.js`:
  ```javascript
  const API_BASE_URL = __DEV__ 
    ? 'http://192.168.1.XXX:8000'  // Replace with your IP
    : 'https://your-production-url.com';
  ```

### Step 3: Start the Backend

Ensure your FastAPI backend is running:

```bash
cd lorebound-backend
# Activate virtual environment if needed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start the React Native App

```bash
cd lorebound
npm start
```

Then in another terminal:

**For Android:**
```bash
npm run android
```

**For iOS:**
```bash
npm run ios
```

## 🔐 Authentication Flow

1. **Registration:**
   - User enters email, username, and password
   - Frontend validates input
   - API call to `/v1/auth/register`
   - Receives access token, refresh token, and user data
   - Tokens stored in AsyncStorage
   - User navigates to MainMenu

2. **Login:**
   - User enters email and password
   - Frontend validates input
   - API call to `/v1/auth/login`
   - Receives access token, refresh token, and user data
   - Tokens stored in AsyncStorage
   - User navigates to MainMenu

3. **Token Storage:**
   - Access token: Used for authenticated API requests
   - Refresh token: Used to get new access tokens when they expire
   - User data: Cached for quick access to user info

## 🛠️ API Service Methods

The `ApiService` class provides these methods:

```javascript
// Login user
await ApiService.login(email, password);

// Register new user
await ApiService.register(email, handle, password);

// Refresh authentication token
await ApiService.refreshToken(refreshToken);

// Get current user profile
await ApiService.getCurrentUser(accessToken);

// Logout user
await ApiService.logout(accessToken);
```

## 🔍 Troubleshooting

### Network Connection Issues

1. **Check Backend is Running:**
   - Visit `http://localhost:8000/docs` in your browser
   - Should see the FastAPI Swagger documentation

2. **Check CORS Settings:**
   - Backend should allow requests from React Native
   - CORS is configured in `lorebound-backend/app/main.py`

3. **Check Network Permissions (Android):**
   - Clear text traffic should be allowed for development
   - Already configured in `android/app/src/main/AndroidManifest.xml`

### Common Errors

**"Network request failed"**
- Backend is not running
- Wrong API URL in `config.js`
- Firewall blocking the connection

**"Invalid email or password"**
- Check user credentials
- Verify user exists in database

**"Registration failed"**
- User might already exist
- Password doesn't meet requirements (min 6 characters)
- Check backend logs for details

## 📱 Testing

1. **Test Registration:**
   - Open the app
   - Switch to "Register" mode
   - Fill in email, username, password
   - Should successfully create account and navigate to MainMenu

2. **Test Login:**
   - Restart the app
   - Enter registered email and password
   - Should successfully login and navigate to MainMenu

3. **Check Storage:**
   - After successful login, tokens are stored
   - Check React Native Debugger or logs for confirmation

## 🔄 Next Steps

To fully implement authentication across the app:

1. **Add Token Refresh Logic:**
   - Implement automatic token refresh when access token expires
   - Add interceptor to handle 401 responses

2. **Protected Routes:**
   - Check for valid token on app start
   - Redirect to AuthScreen if not authenticated
   - Redirect to MainMenu if already authenticated

3. **Logout Functionality:**
   - Add logout button in MainMenu or settings
   - Clear tokens from AsyncStorage
   - Navigate back to AuthScreen

4. **Persistent Login:**
   - Check for saved tokens on app start
   - Validate token with backend
   - Auto-login if token is valid

## 📚 Backend API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎮 API Endpoints Used

- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login user
- `POST /v1/auth/refresh` - Refresh access token
- `GET /v1/auth/me` - Get current user profile
- `POST /v1/auth/logout` - Logout user

All endpoints return standardized response formats as defined in the backend schemas.

