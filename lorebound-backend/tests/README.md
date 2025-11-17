# Test Suite

Comprehensive test suite for LoreBound backend application.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini              # Pytest configuration
├── README.md               # This file
├── legacy/                 # Legacy test suite (moved from root)
├── unit/                   # Unit tests (fast, isolated)
├── integration/            # Integration tests (require database)
├── api/                    # API endpoint tests
├── services/               # Service layer tests
└── fixtures/               # Shared test fixtures and utilities
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# API tests
pytest -m api

# Service tests
pytest -m service

# Exclude slow tests
pytest -m "not slow"
```

### Run specific test files
```bash
pytest tests/unit/test_auth_service.py
pytest tests/api/test_auth_endpoints.py
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests that don't require database or external services.
- Service logic tests
- Utility function tests
- Validation tests

### Integration Tests (`tests/integration/`)
Tests that require database access and test multiple components together.
- Database operations
- Service interactions
- End-to-end workflows

### API Tests (`tests/api/`)
Tests for HTTP endpoints and request/response handling.
- Endpoint availability
- Request validation
- Response formats
- Error handling

### Service Tests (`tests/services/`)
Tests for individual service classes and their methods.
- Business logic
- Error handling
- Edge cases

## Test Markers

- `@pytest.mark.unit` - Unit test
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.api` - API endpoint test
- `@pytest.mark.service` - Service layer test
- `@pytest.mark.slow` - Slow running test
- `@pytest.mark.security` - Security test
- `@pytest.mark.performance` - Performance test
- `@pytest.mark.auth` - Authentication test
- `@pytest.mark.database` - Requires database
- `@pytest.mark.external` - Requires external services

## Writing Tests

### Example Unit Test
```python
import pytest
from app.services.auth_service import AuthenticationService

@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationService:
    def test_password_hashing(self):
        # Test implementation
        pass
```

### Example Integration Test
```python
import pytest
from app.services.auth_service import AuthenticationService

@pytest.mark.integration
@pytest.mark.database
class TestUserRegistration:
    async def test_register_user(self, db_session, sample_user_data):
        # Test implementation
        pass
```

### Example API Test
```python
import pytest
from httpx import AsyncClient

@pytest.mark.api
class TestAuthEndpoints:
    async def test_register_endpoint(self, async_client: AsyncClient):
        # Test implementation
        pass
```

## Legacy Tests

Legacy tests have been moved to `tests/legacy/` and can still be run:
```bash
pytest tests/legacy/
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Pushes to main branch
- Scheduled nightly runs

## Coverage Goals

- Unit tests: >80% coverage
- Integration tests: >70% coverage
- API tests: >90% endpoint coverage
