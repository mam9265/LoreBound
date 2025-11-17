# Authentication Setup Guide

This guide provides step-by-step instructions to get the LoreBound authentication system working from scratch.

## 📋 Prerequisites

Before starting, ensure you have:
- Docker and Docker Compose installed
- Node.js and npm installed
- Android Studio with an emulator
- PowerShell or terminal access

## 🚀 Step-by-Step Setup

### Step 1: Start the Backend Services

Navigate to the backend directory and start all Docker containers:

```powershell
cd lorebound-backend
docker-compose up -d
```

**Expected Output:**
```
✔ Container lorebound-backend-db-1      Healthy
✔ Container lorebound-backend-redis-1   Healthy
✔ Container lorebound-backend-api-1     Started
✔ Container lorebound-backend-worker-1  Started
```

**Verify containers are running:**
```powershell
docker-compose ps
```

All containers should show `Up` or `Up (healthy)` status.

### Step 2: Run Database Migrations

**CRITICAL STEP** - Without this, authentication will fail with "relation users does not exist" error.

```powershell
# Still in lorebound-backend directory
docker-compose exec api poetry run alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 326c0b57e543, Initial migration
```

This creates all necessary database tables including:
- `users` - User accounts
- `profiles` - User profiles
- `inventory` - User items
- `runs` - Game runs
- `leaderboards` - Leaderboard entries

### Step 3: Verify Backend Health

Test that the API is responding:

```powershell
curl http://localhost:8000/healthz
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "dev",
  "database": "connected"
}
```

### Step 4: Start the React Native Frontend

Open a **new PowerShell window** (keep the backend running) and navigate to the frontend directory:

```powershell
cd lorebound
```

**For Android Emulator:**
```powershell
npx react-native run-android
```



The Metro bundler will start automatically. Keep this terminal window open.

### Step 5: Test Registration

1. **Launch the app** on your emulator/device
2. **On the Auth Screen**, tap "Register" (if not already on registration view)
3. **Fill in the form**:
   - Email: `testuser@example.com` (must be unique)
   - Username: `testuser123`
   - Password: `password123` (minimum 6 characters)
   - Confirm Password: `password123`
4. **Tap "Register"**
5. **Expected Result**: 
   - Success alert: "Registration successful! Welcome to LoreBound!"
   - Automatic navigation to Main Menu
   - User tokens stored in AsyncStorage

### Step 6: Test Login

1. **Navigate back to the Auth Screen** (or restart the app)
2. **Switch to Login view** (if needed)
3. **Enter credentials**:
   - Email: `testuser@example.com`
   - Password: `password123`
4. **Tap "Login"**
5. **Expected Result**:
   - Success alert: "Login successful!"
   - Navigation to Main Menu

## 🔍 Monitoring & Debugging

### View Backend Logs

**Watch all API logs in real-time:**
```powershell
cd lorebound-backend
docker-compose logs -f api
```

**View last 50 lines:**
```powershell
docker-compose logs api --tail 50
```

**Successful registration logs look like:**
```
INFO - Registration attempt for email: testuser@example.com
INFO - Attempting to register user with email: testuser@example.com
INFO - Successfully registered user: a6713f53-2c8f-42d4-9de7-d5de33f91dc5
INFO - User registration successful: a6713f53-2c8f-42d4-9de7-d5de33f91dc5
INFO: "POST /v1/auth/register HTTP/1.1" 201 Created
```

### View React Native Logs

The Metro bundler terminal shows:
- Network requests
- Console.log statements
- JavaScript errors

Look for:
```
Login attempt: { email: 'testuser@example.com' }
Login successful: [user-id]
```

### Check Database Tables

Verify tables were created:

```powershell
docker-compose exec db psql -U postgres -d lorebound -c "\dt"
```

**Expected Output:**
```
              List of relations
 Schema |      Name      | Type  |  Owner   
--------+----------------+-------+----------
 public | users          | table | postgres
 public | profiles       | table | postgres
 public | inventory      | table | postgres
 public | runs           | table | postgres
 public | leaderboards   | table | postgres
```

## ❌ Common Issues & Solutions

### Issue 1: "Request timeout" or "Network request failed"

**Cause:** Frontend can't reach backend

**Solutions:**
1. Verify backend is running: `docker-compose ps`
2. Check API health: `curl http://localhost:8000/healthz`
3. For Android emulator: App uses `http://10.0.2.2:8000` (correct)
4. For iOS simulator: App uses `http://localhost:8000` (correct)
5. For physical device: Update `lorebound/src/config/config.js` with your computer's IP address

### Issue 2: "relation 'users' does not exist"

**Cause:** Database migrations not run

**Solution:**
```powershell
cd lorebound-backend
docker-compose exec api poetry run alembic upgrade head
```

### Issue 3: "Email already exists"

**Cause:** Email was previously registered

**Solutions:**
- Use a different email address
- Clear the database:
  ```powershell
  docker-compose down -v  # WARNING: Deletes all data
  docker-compose up -d
  docker-compose exec api poetry run alembic upgrade head
  ```

### Issue 4: CORS Errors

**Cause:** Backend rejecting requests from frontend origin

**Solution:**
The backend is now configured to accept all origins in development mode (`cors_origins = ["*"]`). If you still see CORS errors, restart the backend:

```powershell
docker-compose restart api
```

### Issue 5: Backend won't start / Container unhealthy

**Check logs:**
```powershell
docker-compose logs api
docker-compose logs db
```

**Common fixes:**
```powershell
# Restart all services
docker-compose down
docker-compose up -d

# If database is corrupted
docker-compose down -v  # Removes volumes
docker-compose up -d
docker-compose exec api poetry run alembic upgrade head
```

## 🧪 Testing with Command Line

### Test Registration Endpoint

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/v1/auth/register" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"email":"cli@example.com","handle":"cliuser","password":"testpass123"}'
```

### Test Login Endpoint

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/v1/auth/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"email":"cli@example.com","password":"testpass123"}'
```

### Test Protected Endpoint

First, get an access token from login, then:

```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
Invoke-WebRequest -Uri "http://localhost:8000/v1/auth/me" `
  -Method GET `
  -Headers @{"Authorization"="Bearer $token"}
```

## 🛑 Stopping Services

### Stop Backend (keep data)
```powershell
cd lorebound-backend
docker-compose down
```

### Stop Backend (delete all data)
```powershell
cd lorebound-backend
docker-compose down -v  # WARNING: Removes all database data
```

### Stop React Native
Press `Ctrl+C` in the Metro bundler terminal

## 📝 API Endpoints

All authentication endpoints are prefixed with `/v1/auth`:

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/v1/auth/register` | POST | Register new user | No |
| `/v1/auth/login` | POST | Login user | No |
| `/v1/auth/refresh` | POST | Refresh access token | No |
| `/v1/auth/me` | GET | Get current user | Yes |
| `/v1/auth/logout` | POST | Logout user | Yes |

## 🔐 Configuration

### Backend Configuration

CORS is configured in `lorebound-backend/app/core/config.py`:
```python
cors_origins: List[str] = Field(default=["*"], alias="CORS_ORIGINS")
```

This allows all origins in development. For production, restrict to specific domains.

### Frontend Configuration

API endpoints are configured in `lorebound/src/config/config.js`:
```javascript
const getApiBaseUrl = () => {
  if (__DEV__) {
    if (Platform.OS === 'android') {
      return 'http://10.0.2.2:8000';  // Android emulator
    } else {
      return 'http://localhost:8000';  // iOS simulator
    }
  } else {
    return 'https://your-production-url.com';  // Production
  }
};
```

## ✅ Verification Checklist

Before considering authentication "working", verify:

- [ ] Docker containers are running and healthy
- [ ] Database migrations have been executed
- [ ] Backend health check returns `"status":"healthy"`
- [ ] Frontend app launches without errors
- [ ] Registration creates a new user successfully
- [ ] Login works with registered credentials
- [ ] User is redirected to Main Menu after auth
- [ ] Tokens are stored in AsyncStorage
- [ ] Protected endpoints work with valid tokens

## 🎯 Next Steps

Once authentication is working:

1. **Test token refresh** - Wait 15 minutes and see if token auto-refreshes
2. **Test logout** - Implement and test logout functionality
3. **Test protected routes** - Navigate to other screens requiring auth
4. **Add profile management** - Allow users to update their profiles
5. **Implement password reset** - Add forgot password flow
6. **Add social login** - Configure Apple Sign-In (optional)

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8000/docs` (when backend is running)
- **Backend README**: `lorebound-backend/README.md`
- **Frontend Project Structure**: `lorebound/PROJECT_STRUCTURE.md`
- **Architecture Overview**: `docs/ARCHITECTURE_OVERVIEW.md`

---

**Last Updated:** October 19, 2025

For issues or questions, check the troubleshooting section above or review the backend logs.

