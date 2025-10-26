# How to Run Integration Tests

This guide will walk you through running the Phase 1 & 2 integration tests.

## Prerequisites

Before running tests, ensure:
1. ✅ Docker Desktop is running
2. ✅ Ports 5433, 6379, 8000 are available
3. ✅ PowerShell is available (Windows)

## Quick Start

### Step 1: Start Backend and Seed Data

```powershell
# Navigate to backend
cd lorebound-backend

# Start all services
docker-compose up -d

# Wait for services to be healthy (about 10 seconds)
Start-Sleep -Seconds 10

# Run migrations
docker-compose exec api alembic upgrade head

# Seed content data (dungeons and questions)
docker-compose exec api python scripts/seed_content_data.py
```

### Step 2: Run Integration Tests

```powershell
# Go back to root directory
cd ..

# Run the test script
.\run_integration_tests.ps1
```

## What the Test Script Does

The script automatically tests:

### Backend Services
- ✅ PostgreSQL connection
- ✅ Redis connection  
- ✅ FastAPI health
- ✅ Database migrations

### Phase 1: Dungeon Runs API
- ✅ Get dungeons list
- ✅ Start a new run
- ✅ Get questions
- ✅ Submit run results
- ✅ Get run history
- ✅ Get player stats

### Phase 2: Leaderboard API
- ✅ Get all-time leaderboard
- ✅ Get today's leaderboard
- ✅ Get weekly leaderboard
- ✅ Get user rank with neighbors
- ✅ Get leaderboard statistics
- ✅ Verify Redis caching

## Expected Output

You should see:
- Green `[PASS]` messages for successful tests
- Red `[FAIL]` messages if something goes wrong
- A final summary showing pass/fail counts

Example:
```
[PASS] PostgreSQL
[PASS] Redis
[PASS] FastAPI
[PASS] Migrations
[PASS] StartRun
[PASS] SubmitRun
...

Overall: 14/14 tests passed
```

## Troubleshooting

### Docker not running
```
ERROR: Docker Desktop is not running!
Please start Docker Desktop and try again.
```
**Solution:** Start Docker Desktop and wait for it to fully initialize.

### Port conflicts
```
ERROR: Bind for 0.0.0.0:8000 failed: port is already allocated
```
**Solution:** Stop any services using ports 5433, 6379, or 8000:
```powershell
# Check what's using the port
netstat -ano | findstr :8000

# Stop Docker containers
cd lorebound-backend
docker-compose down
```

### No dungeons found
```
WARNING: No dungeons found. Please seed content data.
```
**Solution:** Run the seed script:
```powershell
cd lorebound-backend
docker-compose exec api python scripts/seed_content_data.py
```

### Authentication fails
If you see authentication errors, the script will automatically create a test user.

### API timeout
```
ERROR: Failed to get dungeons
```
**Solution:** Wait longer for services to start (they need ~10-15 seconds after `docker-compose up`)

## Manual Testing

If you prefer to test manually, you can use the commands from `INTEGRATION_TEST_PLAN.md`.

### Get a token manually:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/register" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","password":"Test123!","handle":"TestUser"}'
  
$token = $response.access_token
```

### Test an endpoint:
```powershell
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/v1/content/dungeons" -Headers $headers
```

## View Logs

To see what's happening in the backend:

```powershell
cd lorebound-backend

# View all logs
docker-compose logs -f

# View just API logs
docker-compose logs -f api

# View just database logs
docker-compose logs -f db
```

## Clean Up

To stop all services after testing:

```powershell
cd lorebound-backend
docker-compose down

# To also remove volumes (fresh start):
docker-compose down -v
```

## Next Steps

After backend tests pass, you can test the frontend:

1. Open a new terminal
2. Navigate to `lorebound` folder
3. Run `npm start`
4. In another terminal, run `npm run android` or `npm run ios`
5. Follow the frontend testing steps in `INTEGRATION_TEST_PLAN.md` (Step 10-14)

## Need Help?

- Check logs: `docker-compose logs -f`
- Verify services: `docker-compose ps`
- Test database: `docker exec -it lorebound-backend-db-1 psql -U postgres -d lorebound`
- Test Redis: `docker exec -it lorebound-backend-redis-1 redis-cli ping`
- Check API health: Visit `http://localhost:8000/docs` in your browser

