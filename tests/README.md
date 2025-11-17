# Root Test Suite

Integration and end-to-end test scripts for the LoreBound project.

## Structure

```
tests/
├── README.md                    # This file
├── legacy/                      # Legacy test scripts (preserved for reference)
├── integration/                 # Integration test scripts
│   ├── test_integration.ps1
│   ├── test_character_customization.ps1
│   └── test_inventory_endpoint.ps1
├── backend/                     # Backend-specific test scripts
│   ├── test_backend.ps1
│   └── test_backend.sh
├── frontend/                     # Frontend-specific test scripts
│   ├── start_frontend_test.ps1
│   └── test_android_connection.ps1
└── scripts/                      # Utility and quick test scripts
    └── quick_test.ps1
```

## Test Scripts

### Integration Tests (`integration/`)

- **`test_integration.ps1`** - Comprehensive integration test suite for Phase 1 & 2 features
  - Tests dungeon runs
  - Tests leaderboards
  - Tests API endpoints

- **`test_character_customization.ps1`** - Character customization API tests
  - Profile endpoints
  - Avatar customization
  - Handle updates

- **`test_inventory_endpoint.ps1`** - Inventory endpoint tests
  - Inventory retrieval
  - Item management

### Backend Tests (`backend/`)

- **`test_backend.ps1`** - PowerShell script for backend endpoint testing
  - Phase 1 & 2 endpoints
  - Health checks
  - Authentication tests

- **`test_backend.sh`** - Shell script for backend endpoint testing (Linux/Mac)

### Frontend Tests (`frontend/`)

- **`start_frontend_test.ps1`** - Frontend test launcher
  - Checks backend connectivity
  - Launches React Native app
  - Android emulator setup

- **`test_android_connection.ps1`** - Android emulator connection diagnostics
  - Backend connectivity
  - Network configuration
  - Emulator status

### Utility Scripts (`scripts/`)

- **`quick_test.ps1`** - Quick connection test for Android emulator
  - Backend status check
  - Connection verification

## Running Tests

### Integration Tests
```powershell
# Run full integration test suite
.\tests\integration\test_integration.ps1

# Test character customization
.\tests\integration\test_character_customization.ps1

# Test inventory endpoint
.\tests\integration\test_inventory_endpoint.ps1
```

### Backend Tests
```powershell
# PowerShell (Windows)
.\tests\backend\test_backend.ps1

# Shell (Linux/Mac)
./tests/backend/test_backend.sh
```

### Frontend Tests
```powershell
# Start frontend testing
.\tests\frontend\start_frontend_test.ps1

# Test Android connection
.\tests\frontend\test_android_connection.ps1
```

### Quick Tests
```powershell
# Quick connection test
.\tests\scripts\quick_test.ps1
```

## Prerequisites

- Docker and Docker Compose (for backend)
- Node.js and npm (for frontend)
- Android Studio with emulator (for Android tests)
- PowerShell (for .ps1 scripts)
- Bash (for .sh scripts)

## Legacy Tests

Legacy test scripts have been moved to `tests/legacy/` and are preserved for reference. These scripts may still work but are not actively maintained.

## Notes

- All PowerShell scripts use `$ErrorActionPreference = "Stop"` or `"Continue"` for error handling
- Scripts assume backend is running on `http://localhost:8000`
- Some scripts require user credentials for testing authenticated endpoints

