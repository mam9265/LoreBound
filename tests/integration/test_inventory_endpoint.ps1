# Test Inventory Endpoint
# Quick test to verify inventory API is working

Write-Host "Testing Inventory API Endpoint" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Test user credentials (update with your actual credentials)
$email = "mdmattern@icloud.com"
Write-Host "Enter your password for $email" -ForegroundColor Yellow
$password = Read-Host -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Login
Write-Host "`n[1/2] Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $email
    password = $plainPassword
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.tokens.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  User ID: $($loginResponse.user.id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get Inventory
Write-Host "`n[2/2] Getting inventory..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $inventory = Invoke-RestMethod -Uri "http://localhost:8000/v1/inventory/" -Method GET -Headers $headers
    Write-Host "✓ Inventory retrieved successfully!" -ForegroundColor Green
    Write-Host "`nInventory Data:" -ForegroundColor Cyan
    Write-Host "  Total Items: $($inventory.total_items)" -ForegroundColor Gray
    Write-Host "  Items Count: $($inventory.items.Count)" -ForegroundColor Gray
    
    if ($inventory.items.Count -gt 0) {
        Write-Host "`nYour Items:" -ForegroundColor Cyan
        foreach ($invItem in $inventory.items) {
            $item = $invItem.item
            $equipped = if ($invItem.equipped) { "✓ EQUIPPED" } else { "" }
            Write-Host "  $($item.slot): $($item.name) ($($item.rarity)) $equipped" -ForegroundColor $(
                switch ($item.rarity) {
                    "common" { "Gray" }
                    "rare" { "Blue" }
                    "epic" { "Magenta" }
                    "legendary" { "Yellow" }
                    default { "White" }
                }
            )
        }
    }
    
    if ($inventory.equipped_items) {
        Write-Host "`nEquipped Items:" -ForegroundColor Cyan
        foreach ($slot in $inventory.equipped_items.PSObject.Properties.Name) {
            $item = $inventory.equipped_items.$slot
            Write-Host "  $slot`: $($item.name) ($($item.rarity))" -ForegroundColor Green
        }
    }
    
    if ($inventory.total_stats) {
        Write-Host "`nTotal Stats:" -ForegroundColor Cyan
        foreach ($stat in $inventory.total_stats.PSObject.Properties.Name) {
            $value = $inventory.total_stats.$stat
            Write-Host "  $stat`: +$value" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Get inventory failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

