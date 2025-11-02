# Quick Connection Test for Android Emulator

Write-Host "=== Android Emulator Connection Test ===" -ForegroundColor Cyan

# Test backend
Write-Host "`n1. Backend Status..." -ForegroundColor Yellow
$api = docker ps --filter "name=lorebound-backend-api-1" --format "{{.Status}}"
if ($api -match "Up") {
    Write-Host "[OK] Backend is running" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backend not running" -ForegroundColor Red
    exit 1
}

# Test health
Write-Host "`n2. API Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -TimeoutSec 3
    Write-Host "[OK] API is healthy" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] API not responding" -ForegroundColor Red
    exit 1
}

# Test auth
Write-Host "`n3. Testing Authentication..." -ForegroundColor Yellow
$body = '{"email":"integrationtest@example.com","password":"TestPass123!"}'
try {
    $auth = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 5
    $token = $auth.tokens.access_token
    Write-Host "[OK] Authentication works" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test dungeons
Write-Host "`n4. Testing Dungeons Endpoint..." -ForegroundColor Yellow
$headers = @{"Authorization" = "Bearer $token"}
try {
    $dungeons = Invoke-RestMethod -Uri "http://localhost:8000/v1/content/dungeons" -Headers $headers -TimeoutSec 5
    Write-Host "[OK] Dungeons endpoint works - Found $($dungeons.Count) dungeons" -ForegroundColor Green
    foreach ($d in $dungeons) {
        Write-Host "  - $($d.title)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ERROR] Dungeons failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test leaderboard
Write-Host "`n5. Testing Leaderboard Endpoint..." -ForegroundColor Yellow
try {
    $url = "http://localhost:8000/v1/leaderboards/?scope=alltime" + "&limit=10"
    $lb = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5
    Write-Host "[OK] Leaderboard works" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Leaderboard failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== All Backend Tests Complete ===" -ForegroundColor Cyan
Write-Host "`nAndroid Emulator Config:" -ForegroundColor Yellow
Write-Host "  Must use: http://10.0.2.2:8000" -ForegroundColor White
Write-Host "  NOT: http://localhost:8000" -ForegroundColor Gray

Write-Host "`nNext Steps in App:" -ForegroundColor Yellow
Write-Host "  1. Make sure you're LOGGED IN" -ForegroundColor White
Write-Host "  2. If token expired, logout and login again" -ForegroundColor White
Write-Host "  3. Check Metro bundler terminal for actual errors" -ForegroundColor White

Write-Host "`nIf app still fails:" -ForegroundColor Yellow
Write-Host "  1. Clear Metro cache: npm start -- --reset-cache" -ForegroundColor White
Write-Host "  2. Rebuild app" -ForegroundColor White
Write-Host "  3. Check what error shows in Metro terminal" -ForegroundColor White

