# Root Test Suite Summary

## Overview

Integration and end-to-end test scripts for the LoreBound project have been organized into logical subdirectories. All original scripts have been preserved and reorganized.

## Structure

```
tests/
├── README.md                    # Main documentation
├── TEST_SUITE_SUMMARY.md        # This file
│
├── legacy/                      # Legacy scripts (documentation only)
│   └── README.md
│
├── integration/                 # Integration test scripts
│   ├── test_integration.ps1           # Full integration test suite
│   ├── test_character_customization.ps1  # Character customization tests
│   └── test_inventory_endpoint.ps1    # Inventory endpoint tests
│
├── backend/                     # Backend-specific test scripts
│   ├── test_backend.ps1         # PowerShell backend tests
│   └── test_backend.sh          # Shell backend tests (Linux/Mac)
│
├── frontend/                    # Frontend-specific test scripts
│   ├── start_frontend_test.ps1  # Frontend test launcher
│   └── test_android_connection.ps1  # Android connection diagnostics
│
└── scripts/                     # Utility and quick test scripts
    └── quick_test.ps1           # Quick connection test
```

## Test Scripts by Category

### Integration Tests (`integration/`)

**`test_integration.ps1`**
- Comprehensive integration test suite
- Tests Phase 1 & 2 features
- Dungeon runs testing
- Leaderboard testing
- API endpoint validation

**`test_character_customization.ps1`**
- Character customization API tests
- Profile endpoint testing
- Avatar customization
- Handle updates

**`test_inventory_endpoint.ps1`**
- Inventory endpoint tests
- Inventory retrieval
- Item management

### Backend Tests (`backend/`)

**`test_backend.ps1`** (PowerShell)
- Backend endpoint testing
- Phase 1 & 2 endpoints
- Health checks
- Authentication tests

**`test_backend.sh`** (Shell)
- Same functionality as PowerShell version
- For Linux/Mac environments

### Frontend Tests (`frontend/`)

**`start_frontend_test.ps1`**
- Frontend test launcher
- Backend connectivity checks
- React Native app launch
- Android emulator setup

**`test_android_connection.ps1`**
- Android emulator connection diagnostics
- Backend connectivity verification
- Network configuration checks
- Emulator status verification

### Utility Scripts (`scripts/`)

**`quick_test.ps1`**
- Quick connection test
- Backend status check
- Connection verification

## Usage Examples

### Run Integration Tests
```powershell
# Full integration suite
.\tests\integration\test_integration.ps1

# Character customization
.\tests\integration\test_character_customization.ps1

# Inventory endpoint
.\tests\integration\test_inventory_endpoint.ps1
```

### Run Backend Tests
```powershell
# Windows
.\tests\backend\test_backend.ps1

# Linux/Mac
./tests/backend/test_backend.sh
```

### Run Frontend Tests
```powershell
# Start frontend testing
.\tests\frontend\start_frontend_test.ps1

# Test Android connection
.\tests\frontend\test_android_connection.ps1
```

### Quick Tests
```powershell
.\tests\scripts\quick_test.ps1
```

## Prerequisites

- **Docker & Docker Compose** - Required for backend testing
- **Node.js & npm** - Required for frontend testing
- **Android Studio** - Required for Android emulator tests
- **PowerShell** - Required for .ps1 scripts (Windows)
- **Bash** - Required for .sh scripts (Linux/Mac)

## Migration Notes

All original test scripts have been reorganized:
- Scripts moved from root `tests/` to appropriate subdirectories
- Legacy directory created for documentation
- Scripts remain functional in their new locations
- Original functionality preserved

## Related Test Suites

- **Backend Unit/Integration Tests**: `lorebound-backend/tests/` - Python pytest suite
- **Root Integration Tests**: `tests/` - PowerShell/Shell scripts (this directory)

Both test suites complement each other:
- Backend tests (`lorebound-backend/tests/`) - Unit tests, service tests, API tests
- Root tests (`tests/`) - End-to-end integration tests, frontend-backend integration

