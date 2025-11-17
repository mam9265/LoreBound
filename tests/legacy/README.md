# Legacy Test Scripts

This directory contains legacy test scripts that have been preserved for reference.

## Contents

- `quick_test.ps1` - Quick connection test (moved to `scripts/`)
- `test_backend.ps1` - Backend test script (moved to `backend/`)
- `test_backend.sh` - Backend test script for Linux/Mac (moved to `backend/`)
- `test_integration.ps1` - Integration test suite (moved to `integration/`)
- `test_character_customization.ps1` - Character customization tests (moved to `integration/`)
- `test_inventory_endpoint.ps1` - Inventory endpoint tests (moved to `integration/`)
- `start_frontend_test.ps1` - Frontend test launcher (moved to `frontend/`)
- `test_android_connection.ps1` - Android connection test (moved to `frontend/`)

## Migration Notes

These scripts have been reorganized into logical subdirectories:
- Integration tests → `tests/integration/`
- Backend tests → `tests/backend/`
- Frontend tests → `tests/frontend/`
- Utility scripts → `tests/scripts/`

The scripts remain functional but are kept here for reference. Use the scripts in their new locations for active testing.

