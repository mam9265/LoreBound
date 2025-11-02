# Backend Testing Script for LoreBound (PowerShell)
# This script helps you quickly test Phase 1 & 2 endpoints

$ErrorActionPreference = "Stop"

# Function to print colored output
function Print-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Print-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Print-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Print-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }

Write-Host "========================================" -ForegroundColor Blue
Write-Host "LoreBound Backend Testing Script" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Check if backend is running
Print-Info "Checking if backend is accessible..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -Method Get -ErrorAction Stop
    Print-Success "Backend is running on http://localhost:8000"
    Write-Host ($health | ConvertTo-Json -Depth 10)
} catch {
    Print-Error "Backend is not accessible. Please start it with: cd lorebound-backend && docker-compose up"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Authentication" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Check if TOKEN environment variable is set
$TOKEN = $env:TOKEN
if (-not $TOKEN) {
    Print-Warning "TOKEN environment variable not set"
    Print-Info "Please set your token: `$env:TOKEN = 'your_access_token'"
    Print-Info ""
    Print-Info "To get a token, use one of these:"
    Write-Host "  1. Login:" -ForegroundColor Yellow
    Write-Host '     $body = @{email="test@example.com"; password="yourpass"} | ConvertTo-Json'
    Write-Host '     $response = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method Post -Body $body -ContentType "application/json"'
    Write-Host '     $env:TOKEN = $response.access_token'
    Write-Host ""
    Write-Host "  2. Register new user:" -ForegroundColor Yellow
    Write-Host '     $body = @{email="test@example.com"; password="Test123!"; handle="TestPlayer"} | ConvertTo-Json'
    Write-Host '     $response = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/register" -Method Post -Body $body -ContentType "application/json"'
    Write-Host '     $env:TOKEN = $response.access_token'
    Write-Host ""
    Print-Info "After setting TOKEN, run this script again"
    exit 0
}

Print-Success "Token found in environment"

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Testing Phase 1: Dungeon Runs" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test 1: Get Dungeons
Print-Info "Test 1: Getting dungeons list..."
try {
    $dungeons = Invoke-RestMethod -Uri "http://localhost:8000/v1/content/dungeons" -Method Get -Headers $headers
    Print-Success "Dungeons endpoint working"
    Print-Info "Found $($dungeons.Count) dungeons"
    
    if ($dungeons.Count -gt 0) {
        $dungeonId = $dungeons[0].id
        Print-Info "Using dungeon ID: $dungeonId"
    }
} catch {
    Print-Error "Dungeons endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 2: Start a Run
Print-Info "Test 2: Starting a new run..."
try {
    $startRunBody = @{
        dungeon_id = $dungeonId
        floor = 1
    } | ConvertTo-Json
    
    $run = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs/start" -Method Post -Headers $headers -Body $startRunBody
    Print-Success "Run started successfully"
    Print-Info "Run ID: $($run.id)"
    $runId = $run.id
} catch {
    Print-Error "Failed to start run: $($_.Exception.Message)"
}

Write-Host ""

# Test 3: Get Questions
Print-Info "Test 3: Getting questions for dungeon..."
try {
    $questions = Invoke-RestMethod -Uri "http://localhost:8000/v1/content/questions?dungeon_id=$dungeonId&count=10" -Method Get -Headers $headers
    Print-Success "Questions endpoint working"
    Print-Info "Got $($questions.Count) questions"
} catch {
    Print-Error "Questions endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 4: Get Run History
Print-Info "Test 4: Getting run history..."
try {
    $history = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs?limit=5" -Method Get -Headers $headers
    Print-Success "Run history endpoint working"
    Print-Info "Found $($history.Count) recent runs"
} catch {
    Print-Warning "Run history endpoint issue: $($_.Exception.Message)"
}

Write-Host ""

# Test 5: Get Run Stats
Print-Info "Test 5: Getting user run statistics..."
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs/stats/me" -Method Get -Headers $headers
    Print-Success "Run stats endpoint working"
    Write-Host ($stats | ConvertTo-Json -Depth 10)
} catch {
    Print-Warning "Run stats endpoint issue: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Testing Phase 2: Leaderboard" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Test 6: All-Time Leaderboard
Print-Info "Test 6: Getting all-time leaderboard..."
try {
    $leaderboard = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" -Method Get -Headers $headers
    Print-Success "Leaderboard endpoint working"
    Print-Info "Total participants: $($leaderboard.total_participants)"
    Print-Info "Entries returned: $($leaderboard.entries.Count)"
} catch {
    Print-Error "Leaderboard endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 7: Today's Leaderboard
Print-Info "Test 7: Getting today's leaderboard..."
try {
    $today = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=today&limit=10" -Method Get -Headers $headers
    Print-Success "Today's leaderboard working"
    Print-Info "Period key: $($today.period_key)"
    Print-Info "Participants today: $($today.total_participants)"
} catch {
    Print-Error "Today's leaderboard failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 8: User Rank
Print-Info "Test 8: Getting your rank..."
try {
    $myRank = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards/me?scope=alltime&neighbors=3" -Method Get -Headers $headers
    Print-Success "User rank endpoint working"
    if ($myRank.rank) {
        Print-Info "Your rank: $($myRank.rank)"
        Print-Info "Your score: $($myRank.score)"
    } else {
        Print-Info "Your rank: No rank yet (complete a run first)"
    }
} catch {
    Print-Error "User rank endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 9: Leaderboard Stats
Print-Info "Test 9: Getting leaderboard statistics..."
try {
    $lbStats = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards/stats?scope=alltime" -Method Get -Headers $headers
    Print-Success "Leaderboard stats endpoint working"
    Write-Host ($lbStats | ConvertTo-Json -Depth 10)
} catch {
    Print-Error "Leaderboard stats endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 10: Redis Caching
Print-Info "Test 10: Testing Redis caching..."
Print-Info "First request (should hit database)..."
$time1 = Measure-Command {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" -Method Get -Headers $headers
}
Write-Host "  Time: $($time1.TotalMilliseconds)ms"

Print-Info "Second request (should hit cache - faster)..."
$time2 = Measure-Command {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" -Method Get -Headers $headers
}
Write-Host "  Time: $($time2.TotalMilliseconds)ms"

if ($time2.TotalMilliseconds -lt $time1.TotalMilliseconds) {
    Print-Success "Cache is working! Second request was faster"
} else {
    Print-Warning "Second request wasn't faster - cache might not be working"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Redis Cache Verification" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

Print-Info "Checking Redis cache keys..."
try {
    $cacheKeys = docker exec lorebound-backend-redis-1 redis-cli KEYS "leaderboard:*" 2>$null
    if ($cacheKeys) {
        Print-Success "Redis cache populated"
        $cacheKeys | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" }
        Print-Info "Found cache keys"
    } else {
        Print-Warning "No cache keys found (this is OK if first run)"
    }
} catch {
    Print-Warning "Could not check Redis: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Print-Success "Backend API tests completed"
Print-Info "Next steps:"
Write-Host "  1. Review any failures above"
Write-Host "  2. Test frontend (npm start && npm run android)"
Write-Host "  3. Complete end-to-end flow testing"
Write-Host ""
Print-Info "For detailed testing instructions, see: INTEGRATION_TEST_PLAN.md"

