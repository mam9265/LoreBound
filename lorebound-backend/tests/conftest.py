"""Simple pytest configuration for basic tests."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    mock = Mock()
    mock.app_env = "test"
    mock.debug = True
    mock.database_url = "sqlite:///test.db"
    mock.redis_url = "redis://localhost:6379/1"
    mock.jwt_algorithm = "RS256"
    mock.cors_origins = ["http://localhost:3000"]
    return mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "handle": "TestPlayer"
    }


@pytest.fixture
def sample_token_data():
    """Sample token data for testing."""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.access_token",
        "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.refresh_token",
        "token_type": "bearer",
        "expires_in": 900
    }
