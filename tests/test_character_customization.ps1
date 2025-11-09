# Test Character Customization Backend Integration
# Run this script to verify the profile endpoints are working

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Character Customization API Tests" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000"
$TEST_EMAIL = "test_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$TEST_PASSWORD = "TestPassword123!"
$TEST_HANDLE = "TestPlayer$(Get-Random -Maximum 9999)"

# Step 1: Register a test user
Write-Host "[1/5] Registering test user..." -ForegroundColor Yellow
$registerBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
    display_name = $TEST_HANDLE
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$API_BASE/v1/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "✓ User registered successfully" -ForegroundColor Green
    Write-Host "  User ID: $($registerResponse.user.id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Login
Write-Host "`n[2/5] Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_BASE/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $accessToken = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Token: $($accessToken.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Get Profile
Write-Host "`n[3/5] Getting user profile..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

try {
    $profileResponse = Invoke-RestMethod -Uri "$API_BASE/v1/profile/" -Method GET -Headers $headers
    Write-Host "✓ Profile retrieved successfully" -ForegroundColor Green
    Write-Host "  Handle: $($profileResponse.handle)" -ForegroundColor Gray
    Write-Host "  Level: $($profileResponse.level)" -ForegroundColor Gray
    Write-Host "  XP: $($profileResponse.xp)" -ForegroundColor Gray
    Write-Host "  Avatar Layers: $($profileResponse.avatar_layers | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Get profile failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Update Character Customization
Write-Host "`n[4/5] Updating character customization..." -ForegroundColor Yellow
$customizationData = @{
    avatar_layers = @{
        equipment = @{
            helmet = "Iron Helm"
            armor = "Chainmail"
            weapon = "Battle Axe"
            shield = "Iron Shield"
        }
        colorIndex = 1
        lastUpdated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
} | ConvertTo-Json -Depth 10

try {
    $updateResponse = Invoke-RestMethod -Uri "$API_BASE/v1/profile/" -Method PUT -Headers $headers -Body $customizationData
    Write-Host "✓ Character customization updated successfully" -ForegroundColor Green
    Write-Host "  Equipment: $($updateResponse.avatar_layers.equipment | ConvertTo-Json -Compress)" -ForegroundColor Gray
    Write-Host "  Color Index: $($updateResponse.avatar_layers.colorIndex)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Update failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Verify Update
Write-Host "`n[5/5] Verifying character customization persisted..." -ForegroundColor Yellow

try {
    $verifyResponse = Invoke-RestMethod -Uri "$API_BASE/v1/profile/" -Method GET -Headers $headers
    
    if ($verifyResponse.avatar_layers.equipment.helmet -eq "Iron Helm" -and 
        $verifyResponse.avatar_layers.colorIndex -eq 1) {
        Write-Host "✓ Character customization verified successfully" -ForegroundColor Green
        Write-Host "  Helmet: $($verifyResponse.avatar_layers.equipment.helmet)" -ForegroundColor Gray
        Write-Host "  Armor: $($verifyResponse.avatar_layers.equipment.armor)" -ForegroundColor Gray
        Write-Host "  Weapon: $($verifyResponse.avatar_layers.equipment.weapon)" -ForegroundColor Gray
        Write-Host "  Shield: $($verifyResponse.avatar_layers.equipment.shield)" -ForegroundColor Gray
        Write-Host "  Color Index: $($verifyResponse.avatar_layers.colorIndex)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Verification failed: Data mismatch" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Verification failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "✓ All tests passed!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "`nCharacter customization backend integration is working correctly!" -ForegroundColor Green
Write-Host "`nTest user credentials:" -ForegroundColor Yellow
Write-Host "  Email: $TEST_EMAIL" -ForegroundColor Gray
Write-Host "  Password: $TEST_PASSWORD" -ForegroundColor Gray
Write-Host "  Handle: $TEST_HANDLE" -ForegroundColor Gray

