# LoreBound Backend Tests

This directory contains comprehensive tests for the LoreBound backend API.

## Test Structure

### Core Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_health.py`** - Health check endpoint tests
- **`test_auth.py`** - Authentication endpoint tests
- **`test_content.py`** - Content management endpoint tests
- **`test_endpoints.py`** - Tests for remaining endpoints (runs, profile, inventory, leaderboards, config)
- **`test_integration.py`** - Integration tests and end-to-end scenarios

## Test Categories

### 1. Unit Tests
- Individual endpoint functionality
- Schema validation
- Input validation and sanitization
- Error handling

### 2. Integration Tests
- Complete user journey flows
- Data consistency across endpoints
- Authentication flows
- Performance under load

### 3. Security Tests
- Input sanitization (XSS, SQL injection)
- Authentication and authorization
- Rate limiting
- Data access controls

### 4. Performance Tests
- Response time validation
- Memory usage monitoring
- Concurrent request handling
- Bulk operation performance

## Running Tests

### Prerequisites
```bash
# Install dependencies
poetry install

# Ensure test database is available
# Tests use in-memory SQLite by default for isolation
```

### Run All Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_auth.py

# Run specific test class
poetry run pytest tests/test_auth.py::TestAuthEndpoints

# Run specific test
poetry run pytest tests/test_auth.py::TestAuthEndpoints::test_register_endpoint_structure
```

### Test Categories
```bash
# Run only integration tests
poetry run pytest tests/test_integration.py

# Run only security tests
poetry run pytest -k "security"

# Run only performance tests
poetry run pytest -k "performance"

# Skip slow tests
poetry run pytest -m "not slow"
```

## Test Configuration

### Environment Variables
Tests use the following environment configuration:
- `APP_ENV=test`
- `DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test_lorebound`
- `REDIS_URL=redis://localhost:6379/1`
- `DEBUG=true`

### Fixtures
The test suite includes several useful fixtures:

#### Database Fixtures
- `async_db_session` - Async database session for tests
- `clean_db` - Clean database state before each test

#### Authentication Fixtures
- `auth_headers` - Pre-configured authentication headers
- `sample_user_data` - Sample user registration data
- `sample_token_data` - Sample JWT token data

#### Mock Fixtures
- `mock_redis` - Mocked Redis client
- `mock_jwt_keys` - Mocked JWT key configuration
- `mock_apple_verification` - Mocked Apple Sign-In verification

## Test Data

### Sample Users
```python
{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "handle": "TestPlayer"
}
```

### Sample Tokens
```python
{
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.access_token",
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.refresh_token",
    "token_type": "bearer",
    "expires_in": 900
}
```

## Test Philosophy

### Current Implementation Status
Since the API endpoints currently contain placeholder implementations (`pass`), the tests focus on:

1. **Endpoint Structure** - Verifying endpoints exist and accept correct HTTP methods
2. **Schema Validation** - Testing Pydantic schemas work correctly
3. **Error Handling** - Ensuring endpoints handle errors gracefully
4. **Security Considerations** - Testing security measures are in place
5. **Performance Characteristics** - Ensuring endpoints perform within bounds

### Future Implementation
As endpoints are implemented, tests should be updated to:

1. **Validate Response Data** - Check actual response content
2. **Test Business Logic** - Verify game mechanics and rules
3. **Database Integration** - Test actual database operations
4. **External Service Integration** - Test Redis, email, etc.

## Best Practices

### Writing Tests
1. **Descriptive Names** - Use clear, descriptive test function names
2. **Arrange-Act-Assert** - Structure tests with clear setup, execution, and verification
3. **Isolation** - Each test should be independent and not rely on others
4. **Realistic Data** - Use realistic test data that represents actual usage

### Test Coverage
- Aim for high test coverage but focus on meaningful tests
- Test both happy path and error scenarios
- Include edge cases and boundary conditions
- Test security and performance aspects

### Performance Testing
- Set reasonable performance expectations
- Test under realistic load conditions
- Monitor memory usage and response times
- Test concurrent user scenarios

## Continuous Integration

### GitHub Actions
The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    poetry install
    poetry run pytest --cov=app --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

### Test Environments
- **Development** - Local testing with real services
- **CI** - Automated testing with mocked services
- **Staging** - Integration testing with staging services
- **Production** - Smoke tests and health checks only

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is running
   - Check connection string in test configuration

2. **Import Errors**
   - Verify all dependencies are installed
   - Check Python path configuration

3. **Async Test Issues**
   - Ensure pytest-asyncio is installed
   - Use `@pytest.mark.asyncio` for async tests

4. **Mock Failures**
   - Verify mock targets are correct
   - Check that mocked functions exist

### Debugging Tests
```bash
# Run with debugging output
poetry run pytest -s -v

# Run with PDB on failures
poetry run pytest --pdb

# Run with detailed traceback
poetry run pytest --tb=long
```

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Add appropriate docstrings
3. Include both positive and negative test cases
4. Update this README if adding new test categories
5. Ensure tests are deterministic and reliable

## Security Testing

### Input Validation
Tests include validation for:
- SQL injection attempts
- XSS payloads
- Path traversal attempts
- Buffer overflow attempts
- Unicode and special character handling

### Authentication Testing
- Token validation and expiration
- Session security
- Rate limiting
- Brute force protection

### Data Protection
- Sensitive data exposure
- Information disclosure
- Data access controls
- Privacy compliance
