# Quick Start Script for Frontend Testing
# This script helps you launch the React Native app for testing

$ErrorActionPreference = "Continue"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " LoreBound Frontend Test Launcher" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if backend is running
Write-Host "`nChecking if backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/healthz" -Method Get -TimeoutSec 3
    if ($response.status -eq "healthy") {
        Write-Host "[OK] Backend is running and healthy" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Backend is running but not healthy" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Backend is not running!" -ForegroundColor Red
    Write-Host "Please start the backend first:" -ForegroundColor Yellow
    Write-Host "  cd lorebound-backend" -ForegroundColor Gray
    Write-Host "  docker-compose up -d" -ForegroundColor Gray
    Write-Host "`nPress Enter to exit..."
    Read-Host
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "lorebound/package.json")) {
    Write-Host "[ERROR] Cannot find lorebound directory" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    Write-Host "`nPress Enter to exit..."
    Read-Host
    exit 1
}

Write-Host "`n[OK] Found lorebound directory" -ForegroundColor Green

# Navigate to lorebound
Set-Location -Path "lorebound"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "`n[INFO] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    Write-Host "This may take a few minutes..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[ERROR] npm install failed" -ForegroundColor Red
        Write-Host "Press Enter to exit..."
        Read-Host
        exit 1
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[OK] Dependencies already installed" -ForegroundColor Green
}

# Check configuration
Write-Host "`nChecking API configuration..." -ForegroundColor Yellow
$configContent = Get-Content "src/config/config.js" -Raw
if ($configContent -match "10\.0\.2\.2:8000" -or $configContent -match "localhost:8000") {
    Write-Host "[OK] API configuration looks correct" -ForegroundColor Green
} else {
    Write-Host "[WARNING] API configuration might need adjustment" -ForegroundColor Yellow
}

# Display instructions
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host " Ready to Launch!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "`nChoose your platform:" -ForegroundColor Yellow
Write-Host "  1. Android Emulator" -ForegroundColor White
Write-Host "  2. iOS Simulator (Mac only)" -ForegroundColor White
Write-Host "  3. Just start Metro Bundler" -ForegroundColor White
Write-Host "  4. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting Metro Bundler and Android..." -ForegroundColor Green
        Write-Host "This will open a new terminal for Metro Bundler" -ForegroundColor Gray
        
        # Start Metro in new terminal
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$pwd'; npm start"
        
        # Wait a moment for Metro to start
        Write-Host "Waiting for Metro Bundler to initialize..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        
        # Start Android
        Write-Host "Launching Android app..." -ForegroundColor Green
        npm run android
    }
    "2" {
        Write-Host "`nStarting Metro Bundler and iOS..." -ForegroundColor Green
        Write-Host "This will open a new terminal for Metro Bundler" -ForegroundColor Gray
        
        # Start Metro in new terminal
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$pwd'; npm start"
        
        # Wait a moment for Metro to start
        Write-Host "Waiting for Metro Bundler to initialize..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        
        # Start iOS
        Write-Host "Launching iOS app..." -ForegroundColor Green
        npm run ios
    }
    "3" {
        Write-Host "`nStarting Metro Bundler..." -ForegroundColor Green
        Write-Host "After Metro starts, run 'npm run android' or 'npm run ios' in another terminal" -ForegroundColor Yellow
        npm start
    }
    "4" {
        Write-Host "`nExiting..." -ForegroundColor Gray
        Set-Location ..
        exit 0
    }
    default {
        Write-Host "`nInvalid choice. Exiting..." -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host " Testing Instructions" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Wait for the app to fully load on your device/emulator" -ForegroundColor White
Write-Host "2. Login with: integrationtest@example.com / TestPass123!" -ForegroundColor White
Write-Host "3. Follow the test steps in FRONTEND_TEST_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Email: integrationtest@example.com" -ForegroundColor Gray
Write-Host "  Password: TestPass123!" -ForegroundColor Gray
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Backend Logs: docker logs lorebound-backend-api-1 -f" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop when done testing" -ForegroundColor Yellow

# Keep script running
Read-Host "`nPress Enter to return to root directory"
Set-Location ..

