# Legacy Test Suite

This directory contains the original test suite that was moved here when the new comprehensive test suite was created.

## Contents

- `test_auth.py` - Original authentication tests
- `test_content.py` - Original content tests
- `test_endpoints.py` - Original endpoint tests
- `test_health.py` - Original health check tests
- `test_integration.py` - Original integration tests
- `test_services.py` - Original service tests
- `test_simple.py` - Original simple tests
- `test_app_structure.py` - Original app structure tests
- `conftest.py` - Original pytest configuration
- `conftest_simple.py` - Simple pytest configuration
- `run_tests.py` - Original test runner script

## Running Legacy Tests

```bash
# Run all legacy tests
pytest tests/legacy/

# Run specific legacy test file
pytest tests/legacy/test_auth.py
```

## Migration Notes

These tests are preserved for reference and backward compatibility. New tests should be written in the main test suite structure:
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/api/` - API endpoint tests
- `tests/services/` - Service layer tests

