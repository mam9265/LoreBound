# Test Android Emulator Connection to Backend
# This script helps diagnose connection issues

Write-Host "=================================" -ForegroundColor Cyan
Write-Host " Android Emulator Connection Test" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Test 1: Backend running?
Write-Host "`n[1] Checking if backend is running..." -ForegroundColor Yellow
$containers = docker ps --filter "name=lorebound-backend-api" --format "{{.Status}}"
if ($containers -match "Up") {
    Write-Host "  ✓ Backend is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend is NOT running!" -ForegroundColor Red
    Write-Host "  Run: cd lorebound-backend; docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Test 2: API Health from localhost
Write-Host "`n[2] Testing API from localhost (host machine)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -Method Get -TimeoutSec 3
    if ($response.status -eq "healthy") {
        Write-Host "  ✓ API responds on localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ API not responding on localhost:8000" -ForegroundColor Red
    exit 1
}

# Test 3: Check if emulator can reach host
Write-Host "`n[3] Android Emulator Network Info..." -ForegroundColor Yellow
Write-Host "  For Android Emulator to reach host:" -ForegroundColor Gray
Write-Host "    - Use: http://10.0.2.2:8000" -ForegroundColor Gray
Write-Host "    - NOT: http://localhost:8000" -ForegroundColor Gray
Write-Host "    - NOT: http://127.0.0.1:8000" -ForegroundColor Gray

# Test 4: Verify config.js
Write-Host "`n[4] Checking config.js..." -ForegroundColor Yellow
$configContent = Get-Content "lorebound/src/config/config.js" -Raw
if ($configContent -match "10\.0\.2\.2:8000") {
    Write-Host "  ✓ Config has correct Android emulator URL (10.0.2.2:8000)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Config might not have correct URL for Android emulator" -ForegroundColor Red
    Write-Host "  Should contain: http://10.0.2.2:8000" -ForegroundColor Yellow
}

# Test 5: Test authentication
Write-Host "`n[5] Testing authentication endpoint..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "integrationtest@example.com"
        password = "TestPass123!"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody `
        -TimeoutSec 5

    if ($loginResponse.tokens.access_token) {
        Write-Host "  ✓ Authentication works" -ForegroundColor Green
        $token = $loginResponse.tokens.access_token
        
        # Test 6: Test dungeons endpoint
        Write-Host "`n[6] Testing dungeons endpoint..." -ForegroundColor Yellow
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        try {
            $dungeons = Invoke-RestMethod `
                -Uri "http://localhost:8000/v1/content/dungeons" `
                -Method Get `
                -Headers $headers `
                -TimeoutSec 5

            Write-Host "  ✓ Dungeons endpoint works - $($dungeons.Count) dungeons found" -ForegroundColor Green
            $dungeons | ForEach-Object {
                Write-Host "    - $($_.title)" -ForegroundColor Gray
            }
        } catch {
            Write-Host "  ✗ Dungeons endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
        }

        # Test 7: Test leaderboard endpoint
        Write-Host "`n[7] Testing leaderboard endpoint..." -ForegroundColor Yellow
        try {
            $leaderboard = Invoke-RestMethod `
                -Uri "http://localhost:8000/v1/leaderboards/?scope=alltime`&limit=10" `
                -Method Get `
                -Headers $headers `
                -TimeoutSec 5

            Write-Host "  ✓ Leaderboard endpoint works" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Leaderboard endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "    Make sure URL has trailing slash: /v1/leaderboards/" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host " Summary & Next Steps" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Write-Host "`nIf all tests passed:" -ForegroundColor Green
Write-Host "  1. Make sure Metro bundler is running (npm start)" -ForegroundColor White
Write-Host "  2. In the app, LOGIN first with:" -ForegroundColor White
Write-Host "     Email: integrationtest@example.com" -ForegroundColor Gray
Write-Host "     Password: TestPass123!" -ForegroundColor Gray
Write-Host "  3. Then navigate to Dungeon Select" -ForegroundColor White

Write-Host "`nCommon issues:" -ForegroundColor Yellow
Write-Host "  - Not logged in → Login/Register first" -ForegroundColor White
Write-Host "  - Token expired → Logout and login again" -ForegroundColor White
Write-Host "  - Wrong URL in config.js → Should be 10.0.2.2:8000 for Android" -ForegroundColor White
Write-Host "  - Metro cache issues → Run: npm start -- --reset-cache" -ForegroundColor White

Write-Host "`nCheck Metro logs for errors when you navigate to Dungeon Select" -ForegroundColor Yellow
Write-Host "The terminal where you ran 'npm start' will show the actual error" -ForegroundColor Gray

Write-Host "`n=================================" -ForegroundColor Cyan

