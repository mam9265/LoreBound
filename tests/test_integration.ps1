# Simple Integration Test Script for LoreBound Phase 1 & 2
# This script tests backend APIs for Dungeon Runs and Leaderboards

$ErrorActionPreference = "Continue"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " LoreBound Integration Test Suite" -ForegroundColor Cyan
Write-Host " Testing Phase 1 & 2" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$TestBlock
    )
    
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    try {
        & $TestBlock
        Write-Host "[PASS] $Name" -ForegroundColor Green
        $script:testsPassed++
        return $true
    } catch {
        Write-Host "[FAIL] $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
        return $false
    }
}

# Change to backend directory
Set-Location -Path "lorebound-backend"

Write-Host "`n=== CHECKING SERVICES ===" -ForegroundColor Cyan

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Gray
try {
    docker ps | Out-Null
    Write-Host "  Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker is not running!" -ForegroundColor Red
    exit 1
}

# Check service health
Write-Host "`nChecking service health..." -ForegroundColor Gray
docker-compose ps

# Test PostgreSQL
Test-Endpoint "PostgreSQL Connection" {
    $result = docker exec lorebound-backend-db-1 psql -U postgres -d lorebound -c "SELECT 1" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL connection failed"
    }
}

# Test Redis
Test-Endpoint "Redis Connection" {
    $result = docker exec lorebound-backend-redis-1 redis-cli ping 2>&1
    if ($result -notmatch "PONG") {
        throw "Redis not responding"
    }
}

# Test FastAPI
Test-Endpoint "FastAPI Health" {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -Method Get -TimeoutSec 5
    if ($response.status -ne "healthy") {
        throw "API not healthy"
    }
}

Write-Host "`n=== TESTING AUTHENTICATION ===" -ForegroundColor Cyan

$token = $null
$testEmail = "integrationtest@example.com"
$testPassword = "TestPass123!"
$testHandle = "IntegrationTester"

# Try login first
Write-Host "Attempting login..." -ForegroundColor Gray
try {
    $loginBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody

    $token = $loginResponse.tokens.access_token
    Write-Host "  Login successful" -ForegroundColor Green
} catch {
    # Try registration
    Write-Host "  Login failed, trying registration..." -ForegroundColor Yellow
    try {
        $registerBody = @{
            email = $testEmail
            password = $testPassword
            handle = $testHandle
        } | ConvertTo-Json

        $registerResponse = Invoke-RestMethod `
            -Uri "http://localhost:8000/v1/auth/register" `
            -Method Post `
            -ContentType "application/json" `
            -Body $registerBody

        $token = $registerResponse.tokens.access_token
        Write-Host "  Registration successful" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Could not authenticate" -ForegroundColor Red
        Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

$headers = @{
    "Authorization" = "Bearer $token"
}

Write-Host "`n=== TESTING PHASE 1: DUNGEON RUNS ===" -ForegroundColor Cyan

# Get Dungeons
$dungeonId = $null
Test-Endpoint "Get Dungeons" {
    $dungeons = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/content/dungeons" `
        -Method Get `
        -Headers $headers

    if ($dungeons.Count -eq 0) {
        throw "No dungeons found"
    }
    
    $script:dungeonId = $dungeons[0].id
    Write-Host "  Found $($dungeons.Count) dungeons" -ForegroundColor Gray
}

# Start a Run
$runId = $null
if ($dungeonId) {
    Test-Endpoint "Start Run" {
        $startBody = @{
            dungeon_id = $dungeonId
            floor = 1
        } | ConvertTo-Json

        $run = Invoke-RestMethod `
            -Uri "http://localhost:8000/v1/runs/start" `
            -Method Post `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $startBody

        $script:runId = $run.id
        Write-Host "  Run ID: $runId" -ForegroundColor Gray
        Write-Host "  Status: $($run.status)" -ForegroundColor Gray
    }
}

# Get Questions
$questions = $null
if ($dungeonId) {
    Test-Endpoint "Get Questions" {
        $url = "http://localhost:8000/v1/content/questions?dungeon_id=$dungeonId" + "&floor=1&count=10"
        $script:questions = Invoke-RestMethod `
            -Uri $url `
            -Method Get `
            -Headers $headers

        if ($questions.Count -eq 0) {
            throw "No questions returned"
        }
        
        Write-Host "  Retrieved $($questions.Count) questions" -ForegroundColor Gray
    }
}

# Submit Run
if ($runId -and $questions -and $questions.Count -gt 0) {
    Test-Endpoint "Submit Run" {
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

        $result = Invoke-RestMethod `
            -Uri "http://localhost:8000/v1/runs/$runId/submit" `
            -Method Post `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $submitBody

        Write-Host "  Status: $($result.status)" -ForegroundColor Gray
        Write-Host "  Score: $($result.total_score)" -ForegroundColor Gray
    }
}

# Get Run History
Test-Endpoint "Get Run History" {
    $history = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/runs/?limit=10" `
        -Method Get `
        -Headers $headers

    Write-Host "  Found $($history.runs.Count) runs" -ForegroundColor Gray
}

# Get Run Stats
Test-Endpoint "Get Run Stats" {
    $stats = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/runs/stats/me" `
        -Method Get `
        -Headers $headers

    Write-Host "  Total Runs: $($stats.total_runs)" -ForegroundColor Gray
    Write-Host "  Total Score: $($stats.total_score)" -ForegroundColor Gray
    Write-Host "  Average: $($stats.average_score)" -ForegroundColor Gray
}

Write-Host "`n=== TESTING PHASE 2: LEADERBOARD ===" -ForegroundColor Cyan

# All-Time Leaderboard
Test-Endpoint "All-Time Leaderboard" {
    $url = "http://localhost:8000/v1/leaderboards/?scope=alltime" + "&limit=10"
    $leaderboard = Invoke-RestMethod `
        -Uri $url `
        -Method Get `
        -Headers $headers

    Write-Host "  Participants: $($leaderboard.total_participants)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboard.entries.Count)" -ForegroundColor Gray
}

# Today's Leaderboard
Test-Endpoint "Today's Leaderboard" {
    $url = "http://localhost:8000/v1/leaderboards/?scope=today" + "&limit=10"
    $leaderboard = Invoke-RestMethod `
        -Uri $url `
        -Method Get `
        -Headers $headers

    Write-Host "  Period: $($leaderboard.period_key)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboard.entries.Count)" -ForegroundColor Gray
}

# Weekly Leaderboard
Test-Endpoint "Weekly Leaderboard" {
    $url = "http://localhost:8000/v1/leaderboards/?scope=weekly" + "&limit=10"
    $leaderboard = Invoke-RestMethod `
        -Uri $url `
        -Method Get `
        -Headers $headers

    Write-Host "  Period: $($leaderboard.period_key)" -ForegroundColor Gray
    Write-Host "  Entries: $($leaderboard.entries.Count)" -ForegroundColor Gray
}

# User Rank
Test-Endpoint "Get User Rank" {
    $url = "http://localhost:8000/v1/leaderboards/me?scope=alltime" + "&neighbors=3"
    $userRank = Invoke-RestMethod `
        -Uri $url `
        -Method Get `
        -Headers $headers

    if ($userRank.rank) {
        Write-Host "  Your Rank: $($userRank.rank)" -ForegroundColor Gray
        Write-Host "  Your Score: $($userRank.score)" -ForegroundColor Gray
    } else {
        Write-Host "  No rank yet" -ForegroundColor Gray
    }
}

# Leaderboard Stats
Test-Endpoint "Leaderboard Stats" {
    $stats = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/leaderboards/stats?scope=alltime" `
        -Method Get `
        -Headers $headers

    Write-Host "  Participants: $($stats.participants)" -ForegroundColor Gray
    Write-Host "  Average Score: $($stats.average_score)" -ForegroundColor Gray
    Write-Host "  Highest Score: $($stats.highest_score)" -ForegroundColor Gray
}

# Redis Caching Test
Test-Endpoint "Redis Caching" {
    $url = "http://localhost:8000/v1/leaderboards/?scope=alltime" + "&limit=10"
    
    # First request
    $stopwatch1 = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-RestMethod -Uri $url -Method Get -Headers $headers | Out-Null
    $stopwatch1.Stop()
    $time1 = $stopwatch1.ElapsedMilliseconds

    # Second request (should be cached)
    $stopwatch2 = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-RestMethod -Uri $url -Method Get -Headers $headers | Out-Null
    $stopwatch2.Stop()
    $time2 = $stopwatch2.ElapsedMilliseconds

    Write-Host "  First request: ${time1}ms" -ForegroundColor Gray
    Write-Host "  Second request: ${time2}ms" -ForegroundColor Gray
    
    if ($time2 -lt $time1) {
        Write-Host "  Cache is working!" -ForegroundColor Green
    }
}

# Return to root
Set-Location ..

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host " TEST RESULTS" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
$total = $testsPassed + $testsFailed
Write-Host "Total: $total" -ForegroundColor Gray

if ($testsFailed -eq 0) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome tests failed." -ForegroundColor Yellow
    exit 1
}

