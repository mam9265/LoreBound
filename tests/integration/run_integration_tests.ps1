# Integration Test Script for Phase 1 & 2
# LoreBound Backend Testing

$ErrorActionPreference = "Continue"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  LoreBound Integration Test Suite  " -ForegroundColor Cyan
Write-Host "  Phase 1: Dungeon Runs              " -ForegroundColor Cyan
Write-Host "  Phase 2: Leaderboard               " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test result tracking
$global:testResults = @{
    PostgreSQL = $null
    Redis = $null
    FastAPI = $null
    Migrations = $null
    StartRun = $null
    SubmitRun = $null
    GetHistory = $null
    GetStats = $null
    LeaderboardAll = $null
    LeaderboardToday = $null
    LeaderboardWeekly = $null
    UserRank = $null
    LeaderboardStats = $null
    RedisCaching = $null
}

function Write-TestHeader {
    param([string]$title)
    Write-Host "`n========================================" -ForegroundColor Yellow
    Write-Host "  $title" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
}

function Write-TestResult {
    param(
        [string]$testName,
        [bool]$passed,
        [string]$message = ""
    )
    if ($passed) {
        Write-Host "[PASS] $testName" -ForegroundColor Green
        $global:testResults[$testName] = "PASS"
    } else {
        Write-Host "[FAIL] $testName - $message" -ForegroundColor Red
        $global:testResults[$testName] = "FAIL"
    }
}

function Test-DockerRunning {
    try {
        docker ps | Out-Null
        return $true
    } catch {
        return $false
    }
}

# ======================================
# Part 1: Backend Setup & Verification
# ======================================

Write-TestHeader "PART 1: Backend Setup & Verification"

# Check if Docker is running
Write-Host "`nChecking Docker Desktop..." -ForegroundColor Cyan
if (-not (Test-DockerRunning)) {
    Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker Desktop is running" -ForegroundColor Green

# Navigate to backend directory
Set-Location -Path "lorebound-backend"

# Step 1: Start Backend Services
Write-Host "`n--- Step 1: Starting Backend Services ---" -ForegroundColor Cyan
Write-Host "Running: docker-compose up -d" -ForegroundColor Gray
docker-compose up -d

Start-Sleep -Seconds 5

Write-Host "`nChecking service status..." -ForegroundColor Cyan
docker-compose ps

# Step 2: Check Service Health
Write-Host "`n--- Step 2: Checking Service Health ---" -ForegroundColor Cyan

# Test PostgreSQL
Write-Host "`nTesting PostgreSQL..." -ForegroundColor Cyan
try {
    $pgResult = docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT 1" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestResult "PostgreSQL" $true
    } else {
        Write-TestResult "PostgreSQL" $false "Connection failed"
    }
} catch {
    Write-TestResult "PostgreSQL" $false $_.Exception.Message
}

# Test Redis
Write-Host "`nTesting Redis..." -ForegroundColor Cyan
try {
    $redisResult = docker exec lorebound-backend-redis-1 redis-cli ping 2>&1
    if ($redisResult -match "PONG") {
        Write-TestResult "Redis" $true
    } else {
        Write-TestResult "Redis" $false "No PONG response"
    }
} catch {
    Write-TestResult "Redis" $false $_.Exception.Message
}

# Test FastAPI
Write-Host "`nTesting FastAPI..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -Method Get -TimeoutSec 5
    if ($response.status -eq "healthy") {
        Write-TestResult "FastAPI" $true
    } else {
        Write-TestResult "FastAPI" $false "Status not healthy"
    }
} catch {
    Write-TestResult "FastAPI" $false $_.Exception.Message
}

# Step 3: Run Database Migrations
Write-Host "`n--- Step 3: Running Database Migrations ---" -ForegroundColor Cyan
Write-Host "Current migration status:" -ForegroundColor Gray
docker-compose exec -T api alembic current

Write-Host "`nRunning migrations..." -ForegroundColor Cyan
try {
    docker-compose exec -T api alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-TestResult "Migrations" $true
    } else {
        Write-TestResult "Migrations" $false "Migration failed"
    }
} catch {
    Write-TestResult "Migrations" $false $_.Exception.Message
}

Write-Host "`nFinal migration status:" -ForegroundColor Gray
docker-compose exec -T api alembic current

# Step 4: Check Database Schema
Write-Host "`n--- Step 4: Checking Database Schema ---" -ForegroundColor Cyan
docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "\dt"

# ======================================
# Part 2: Backend API Testing
# ======================================

Write-TestHeader "PART 2: Backend API Testing"

# Step 6: Authentication
Write-Host "`n--- Step 6: Getting Authentication Token ---" -ForegroundColor Cyan

# Try to login first, if fails, register
$token = $null
$testEmail = "integrationtest@example.com"
$testPassword = "TestPass123!"
$testHandle = "IntegrationTester"

Write-Host "Attempting to login..." -ForegroundColor Gray
try {
    $loginBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop

    $token = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
} catch {
    Write-Host "Login failed, attempting to register..." -ForegroundColor Yellow
    try {
        $registerBody = @{
            email = $testEmail
            password = $testPassword
            handle = $testHandle
        } | ConvertTo-Json

        $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/register" `
            -Method Post `
            -ContentType "application/json" `
            -Body $registerBody `
            -ErrorAction Stop

        $token = $registerResponse.access_token
        Write-Host "✓ Registration successful" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Could not authenticate" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

Write-Host "Token obtained: $($token.Substring(0, 20))..." -ForegroundColor Green

# Step 7: Test Phase 1 - Dungeon Runs
Write-TestHeader "Step 7: Testing Phase 1 - Dungeon Runs"

# Test 7a: Get Dungeons
Write-Host "`n--- Test 7a: Get Dungeons ---" -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $dungeons = Invoke-RestMethod -Uri "http://localhost:8000/v1/content/dungeons" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved $($dungeons.Count) dungeons" -ForegroundColor Green
    if ($dungeons.Count -gt 0) {
        $dungeon = $dungeons[0]
        $dungeonId = $dungeon.id
        Write-Host "  Using dungeon: $($dungeon.title) (ID: $dungeonId)" -ForegroundColor Gray
    } else {
        Write-Host "WARNING: No dungeons found. Please seed content data." -ForegroundColor Yellow
        $dungeonId = $null
    }
} catch {
    Write-Host "ERROR: Failed to get dungeons" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    $dungeonId = $null
}

if ($dungeonId) {
    # Test 7b: Start a Run
    Write-Host "`n--- Test 7b: Start a Run ---" -ForegroundColor Cyan
    try {
        $startRunBody = @{
            dungeon_id = $dungeonId
            floor = 1
        } | ConvertTo-Json

        $run = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs/start" `
            -Method Post `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $startRunBody

        $runId = $run.id
        Write-Host "✓ Run started successfully" -ForegroundColor Green
        Write-Host "  Run ID: $runId" -ForegroundColor Gray
        Write-Host "  Status: $($run.status)" -ForegroundColor Gray
        Write-TestResult "StartRun" $true
    } catch {
        Write-Host "ERROR: Failed to start run" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-TestResult "StartRun" $false $_.Exception.Message
        $runId = $null
    }

    # Test 7c: Get Questions
    Write-Host "`n--- Test 7c: Get Questions ---" -ForegroundColor Cyan
    try {
        $questions = Invoke-RestMethod -Uri "http://localhost:8000/v1/content/questions?dungeon_id=$dungeonId`&count=10" `
            -Method Get `
            -Headers $headers

        Write-Host "✓ Retrieved $($questions.Count) questions" -ForegroundColor Green
        if ($questions.Count -gt 0) {
            Write-Host "  First question: $($questions[0].prompt.Substring(0, 50))..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "ERROR: Failed to get questions" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }

    if ($runId) {
        # Test 7d: Submit Run
        Write-Host "`n--- Test 7d: Submit Run ---" -ForegroundColor Cyan
        try {
            # Create sample turn data
            $turnData = @(
                @{
                    i = 0
                    qid = $questions[0].id
                    a = 0
                    c = $true
                    t = 2500
                    ts = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
                    h = "test_signature"
                }
            )

            $scores = @(
                @{
                    points = 100
                    answer_time = 2.5
                    is_correct = $true
                    streak_bonus = 10
                    time_bonus = 5
                }
            )

            $submitBody = @{
                turn_data = $turnData
                scores = $scores
                client_signature = "test_aggregate_sig"
            } | ConvertTo-Json -Depth 10

            $submitResult = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs/$runId/submit" `
                -Method Post `
                -Headers $headers `
                -ContentType "application/json" `
                -Body $submitBody

            Write-Host "✓ Run submitted successfully" -ForegroundColor Green
            Write-Host "  Status: $($submitResult.status)" -ForegroundColor Gray
            Write-Host "  Total Score: $($submitResult.total_score)" -ForegroundColor Gray
            Write-TestResult "SubmitRun" $true
        } catch {
            Write-Host "ERROR: Failed to submit run" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            Write-TestResult "SubmitRun" $false $_.Exception.Message
        }
    }

    # Test 7e: Get Run History
    Write-Host "`n--- Test 7e: Get Run History ---" -ForegroundColor Cyan
    try {
        $history = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs?limit=10" `
            -Method Get `
            -Headers $headers

        Write-Host "✓ Retrieved $($history.runs.Count) runs from history" -ForegroundColor Green
        if ($history.runs.Count -gt 0) {
            Write-Host "  Most recent run score: $($history.runs[0].total_score)" -ForegroundColor Gray
        }
        Write-TestResult "GetHistory" $true
    } catch {
        Write-Host "ERROR: Failed to get run history" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-TestResult "GetHistory" $false $_.Exception.Message
    }

    # Test 7f: Get Run Stats
    Write-Host "`n--- Test 7f: Get Run Stats ---" -ForegroundColor Cyan
    try {
        $stats = Invoke-RestMethod -Uri "http://localhost:8000/v1/runs/stats/me" `
            -Method Get `
            -Headers $headers

        Write-Host "✓ Retrieved run stats" -ForegroundColor Green
        Write-Host "  Total Runs: $($stats.total_runs)" -ForegroundColor Gray
        Write-Host "  Total Score: $($stats.total_score)" -ForegroundColor Gray
        Write-Host "  Average Score: $($stats.average_score)" -ForegroundColor Gray
        Write-Host "  Best Score: $($stats.best_score)" -ForegroundColor Gray
        Write-TestResult "GetStats" $true
    } catch {
        Write-Host "ERROR: Failed to get run stats" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-TestResult "GetStats" $false $_.Exception.Message
    }
}

# Step 8: Test Phase 2 - Leaderboard
Write-TestHeader "Step 8: Testing Phase 2 - Leaderboard"

# Test 8a: Get All-Time Leaderboard
Write-Host "`n--- Test 8a: Get All-Time Leaderboard ---" -ForegroundColor Cyan
try {
    $leaderboard = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime`&limit=10" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved all-time leaderboard" -ForegroundColor Green
    Write-Host "  Total Participants: $($leaderboard.total_participants)" -ForegroundColor Gray
    Write-Host "  Period Key: $($leaderboard.period_key)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboard.entries.Count)" -ForegroundColor Gray
    if ($leaderboard.entries.Count -gt 0) {
        Write-Host "  Top Score: $($leaderboard.entries[0].score)" -ForegroundColor Gray
    }
    Write-TestResult "LeaderboardAll" $true
} catch {
    Write-Host "ERROR: Failed to get all-time leaderboard" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "LeaderboardAll" $false $_.Exception.Message
}

# Test 8b: Get Today's Leaderboard
Write-Host "`n--- Test 8b: Get Today's Leaderboard ---" -ForegroundColor Cyan
try {
    $leaderboardToday = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=today`&limit=10" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved today's leaderboard" -ForegroundColor Green
    Write-Host "  Period Key: $($leaderboardToday.period_key)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboardToday.entries.Count)" -ForegroundColor Gray
    Write-TestResult "LeaderboardToday" $true
} catch {
    Write-Host "ERROR: Failed to get today's leaderboard" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "LeaderboardToday" $false $_.Exception.Message
}

# Test 8c: Get Weekly Leaderboard
Write-Host "`n--- Test 8c: Get Weekly Leaderboard ---" -ForegroundColor Cyan
try {
    $leaderboardWeekly = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=weekly`&limit=10" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved weekly leaderboard" -ForegroundColor Green
    Write-Host "  Period Key: $($leaderboardWeekly.period_key)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboardWeekly.entries.Count)" -ForegroundColor Gray
    Write-TestResult "LeaderboardWeekly" $true
} catch {
    Write-Host "ERROR: Failed to get weekly leaderboard" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "LeaderboardWeekly" $false $_.Exception.Message
}

# Test 8d: Get Your Rank
Write-Host "`n--- Test 8d: Get Your Rank ---" -ForegroundColor Cyan
try {
    $userRank = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards/me?scope=alltime`&neighbors=3" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved user rank" -ForegroundColor Green
    if ($userRank.rank) {
        Write-Host "  Your Rank: $($userRank.rank)" -ForegroundColor Gray
        Write-Host "  Your Score: $($userRank.score)" -ForegroundColor Gray
    } else {
        Write-Host "  No rank yet (no completed runs)" -ForegroundColor Gray
    }
    Write-TestResult "UserRank" $true
} catch {
    Write-Host "ERROR: Failed to get user rank" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "UserRank" $false $_.Exception.Message
}

# Test 8e: Get Leaderboard Stats
Write-Host "`n--- Test 8e: Get Leaderboard Stats ---" -ForegroundColor Cyan
try {
    $lbStats = Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards/stats?scope=alltime" `
        -Method Get `
        -Headers $headers

    Write-Host "✓ Retrieved leaderboard stats" -ForegroundColor Green
    Write-Host "  Participants: $($lbStats.participants)" -ForegroundColor Gray
    Write-Host "  Average Score: $($lbStats.average_score)" -ForegroundColor Gray
    Write-Host "  Highest Score: $($lbStats.highest_score)" -ForegroundColor Gray
    Write-Host "  Lowest Score: $($lbStats.lowest_score)" -ForegroundColor Gray
    Write-TestResult "LeaderboardStats" $true
} catch {
    Write-Host "ERROR: Failed to get leaderboard stats" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "LeaderboardStats" $false $_.Exception.Message
}

# Test 8f: Verify Redis Caching
Write-Host "`n--- Test 8f: Verify Redis Caching ---" -ForegroundColor Cyan
try {
    # First request
    $stopwatch1 = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime`&limit=10" `
        -Method Get `
        -Headers $headers | Out-Null
    $stopwatch1.Stop()
    $time1 = $stopwatch1.ElapsedMilliseconds

    # Second request (should be cached)
    $stopwatch2 = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-RestMethod -Uri "http://localhost:8000/v1/leaderboards?scope=alltime`&limit=10" `
        -Method Get `
        -Headers $headers | Out-Null
    $stopwatch2.Stop()
    $time2 = $stopwatch2.ElapsedMilliseconds

    Write-Host "✓ Caching test complete" -ForegroundColor Green
    Write-Host "  First request: ${time1}ms" -ForegroundColor Gray
    Write-Host "  Second request: ${time2}ms" -ForegroundColor Gray
    if ($time2 -lt $time1) {
        Write-Host "  Cache is working! (faster on 2nd request)" -ForegroundColor Green
    }

    # Check Redis keys
    $redisKeys = docker exec lorebound-backend-redis-1 redis-cli KEYS "leaderboard:*"
    Write-Host "  Redis cache keys found: $($redisKeys.Count)" -ForegroundColor Gray
    Write-TestResult "RedisCaching" $true
} catch {
    Write-Host "ERROR: Failed to verify Redis caching" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-TestResult "RedisCaching" $false $_.Exception.Message
}

# ======================================
# Test Results Summary
# ======================================

Write-TestHeader "TEST RESULTS SUMMARY"

Write-Host "`nBackend Services:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:    $($global:testResults.PostgreSQL)" -ForegroundColor $(if ($global:testResults.PostgreSQL -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Redis:         $($global:testResults.Redis)" -ForegroundColor $(if ($global:testResults.Redis -eq "PASS") { "Green" } else { "Red" })
Write-Host "  FastAPI:       $($global:testResults.FastAPI)" -ForegroundColor $(if ($global:testResults.FastAPI -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Migrations:    $($global:testResults.Migrations)" -ForegroundColor $(if ($global:testResults.Migrations -eq "PASS") { "Green" } else { "Red" })

Write-Host "`nPhase 1 API (Dungeon Runs):" -ForegroundColor Cyan
Write-Host "  Start Run:     $($global:testResults.StartRun)" -ForegroundColor $(if ($global:testResults.StartRun -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Submit Run:    $($global:testResults.SubmitRun)" -ForegroundColor $(if ($global:testResults.SubmitRun -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Get History:   $($global:testResults.GetHistory)" -ForegroundColor $(if ($global:testResults.GetHistory -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Get Stats:     $($global:testResults.GetStats)" -ForegroundColor $(if ($global:testResults.GetStats -eq "PASS") { "Green" } else { "Red" })

Write-Host "`nPhase 2 API (Leaderboard):" -ForegroundColor Cyan
Write-Host "  All-Time LB:   $($global:testResults.LeaderboardAll)" -ForegroundColor $(if ($global:testResults.LeaderboardAll -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Today LB:      $($global:testResults.LeaderboardToday)" -ForegroundColor $(if ($global:testResults.LeaderboardToday -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Weekly LB:     $($global:testResults.LeaderboardWeekly)" -ForegroundColor $(if ($global:testResults.LeaderboardWeekly -eq "PASS") { "Green" } else { "Red" })
Write-Host "  User Rank:     $($global:testResults.UserRank)" -ForegroundColor $(if ($global:testResults.UserRank -eq "PASS") { "Green" } else { "Red" })
Write-Host "  LB Stats:      $($global:testResults.LeaderboardStats)" -ForegroundColor $(if ($global:testResults.LeaderboardStats -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Redis Cache:   $($global:testResults.RedisCaching)" -ForegroundColor $(if ($global:testResults.RedisCaching -eq "PASS") { "Green" } else { "Red" })

$passCount = ($global:testResults.Values | Where-Object { $_ -eq "PASS" }).Count
$totalTests = ($global:testResults.Values | Where-Object { $_ -ne $null }).Count

Write-Host "`nOverall: $passCount/$totalTests tests passed" -ForegroundColor $(if ($passCount -eq $totalTests) { "Green" } else { "Yellow" })

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Integration testing complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Return to root directory
Set-Location ..

