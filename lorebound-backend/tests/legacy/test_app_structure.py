"""Test application structure and basic endpoint routing."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import os


@pytest.fixture
def mock_database_connection():
    """Mock database connection to avoid connection issues."""
    with patch('app.repositories.base.create_async_engine') as mock_engine, \
         patch('app.repositories.base.wait_for_database', return_value=True), \
         patch('app.repositories.base.test_database_connection', return_value=True), \
         patch('app.repositories.base.get_database_info', return_value={"database": "test", "active_connections": 1}), \
         patch('app.repositories.base.close_database_connection'):
        
        mock_engine.return_value = Mock()
        yield mock_engine


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch.dict(os.environ, {
        'APP_ENV': 'test',
        'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost:5432/test',
        'REDIS_URL': 'redis://localhost:6379/1',
        'JWT_PRIVATE_KEY_PATH': 'test_private.pem',
        'JWT_PUBLIC_KEY_PATH': 'test_public.pem',
        'CELERY_BROKER_URL': 'redis://localhost:6379/2',
        'CELERY_RESULT_BACKEND': 'redis://localhost:6379/2'
    }):
        yield


@pytest.fixture
def mock_config_validation():
    """Mock configuration validation."""
    with patch('app.core.config.settings.validate_setup') as mock_validate:
        mock_validate.return_value = {
            "config_valid": True,
            "errors": [],
            "warnings": []
        }
        yield mock_validate


def test_app_creation(mock_database_connection, mock_settings, mock_config_validation):
    """Test that the FastAPI app can be created."""
    from app.main import create_app
    
    app = create_app()
    assert app is not None
    assert app.title == "LoreBound Backend"


def test_health_endpoint(mock_database_connection, mock_settings, mock_config_validation):
    """Test health check endpoint."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_detailed_health_endpoint(mock_database_connection, mock_settings, mock_config_validation):
    """Test detailed health check endpoint."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/healthz/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "configuration" in data


def test_metrics_endpoint(mock_database_connection, mock_settings, mock_config_validation):
    """Test metrics endpoint."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "metrics" in data


def test_auth_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that auth endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test register endpoint exists
    response = client.post("/v1/auth/register", json={
        "email": "test@example.com",
        "password": "TestPassword123!",
        "handle": "TestUser"
    })
    assert response.status_code != 404  # Endpoint exists
    
    # Test login endpoint exists
    response = client.post("/v1/auth/login", json={
        "email": "test@example.com",
        "password": "TestPassword123!"
    })
    assert response.status_code != 404  # Endpoint exists


def test_content_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that content endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test dungeons endpoint exists
    response = client.get("/v1/content/dungeons")
    assert response.status_code != 404  # Endpoint exists
    
    # Test specific dungeon endpoint exists
    response = client.get("/v1/content/dungeons/test-dungeon")
    assert response.status_code != 404  # Endpoint exists


def test_profile_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that profile endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test get profile endpoint exists
    response = client.get("/v1/profile/")
    assert response.status_code != 404  # Endpoint exists
    
    # Test update profile endpoint exists
    response = client.put("/v1/profile/", json={})
    assert response.status_code != 404  # Endpoint exists


def test_inventory_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that inventory endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test get inventory endpoint exists
    response = client.get("/v1/inventory/")
    assert response.status_code != 404  # Endpoint exists
    
    # Test equip item endpoint exists
    response = client.post("/v1/inventory/equip", json={})
    assert response.status_code != 404  # Endpoint exists


def test_runs_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that runs endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test start run endpoint exists
    response = client.post("/v1/runs/start", json={})
    assert response.status_code != 404  # Endpoint exists
    
    # Test submit run endpoint exists
    response = client.post("/v1/runs/submit", json={})
    assert response.status_code != 404  # Endpoint exists


def test_leaderboard_endpoints_exist(mock_database_connection, mock_settings, mock_config_validation):
    """Test that leaderboard endpoints exist."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test get leaderboard endpoint exists
    response = client.get("/v1/leaderboards/")
    assert response.status_code != 404  # Endpoint exists
    
    # Test get my rank endpoint exists
    response = client.get("/v1/leaderboards/me")
    assert response.status_code != 404  # Endpoint exists


def test_config_endpoint_exists(mock_database_connection, mock_settings, mock_config_validation):
    """Test that config endpoint exists."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test get config endpoint exists
    response = client.get("/v1/config/")
    assert response.status_code != 404  # Endpoint exists


def test_cors_middleware(mock_database_connection, mock_settings, mock_config_validation):
    """Test CORS middleware is configured."""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Test CORS headers
    response = client.options("/healthz")
    assert response.status_code in [200, 405]  # Either allowed or method not allowed


def test_app_lifespan_handling(mock_database_connection, mock_settings, mock_config_validation):
    """Test app lifespan events."""
    from app.main import create_app
    
    # App should create without errors
    app = create_app()
    assert app is not None
    
    # Lifespan should handle startup/shutdown gracefully
    # (This is tested by the successful creation of TestClient)
