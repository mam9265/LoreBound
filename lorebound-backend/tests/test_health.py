"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_healthy(self, client: TestClient):
        """Test health check when everything is healthy."""
        with patch('app.repositories.base.test_database_connection', return_value=True), \
             patch('app.repositories.base.get_database_info', return_value={
                 "database": "test_lorebound",
                 "active_connections": 5
             }):
            
            response = client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "0.1.0"
            assert data["database"] == "connected"
            assert "database_info" in data
            assert data["database_info"]["database"] == "test_lorebound"
            assert data["database_info"]["active_connections"] == 5

    def test_health_check_unhealthy_database(self, client: TestClient):
        """Test health check when database is unhealthy."""
        with patch('app.repositories.base.test_database_connection', return_value=False):
            
            response = client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "database_info" not in data

    def test_health_check_database_info_error(self, client: TestClient):
        """Test health check when database info retrieval fails."""
        with patch('app.repositories.base.test_database_connection', return_value=True), \
             patch('app.repositories.base.get_database_info', side_effect=Exception("DB info error")):
            
            response = client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert "database_info" not in data

    def test_detailed_health_check_healthy(self, client: TestClient):
        """Test detailed health check when everything is healthy."""
        mock_config_validation = {
            "config_valid": True,
            "errors": [],
            "warnings": []
        }
        
        with patch('app.repositories.base.test_database_connection', return_value=True), \
             patch('app.repositories.base.get_database_info', return_value={
                 "database": "test_lorebound",
                 "active_connections": 5,
                 "version": "13.0"
             }), \
             patch('app.core.config.settings.validate_setup', return_value=mock_config_validation):
            
            response = client.get("/healthz/detailed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "0.1.0"
            assert data["environment"] == "test"
            assert "timestamp" in data
            
            # Database health
            assert data["database"]["connected"] is True
            assert data["database"]["info"]["database"] == "test_lorebound"
            assert data["database"]["info"]["active_connections"] == 5
            
            # Configuration health
            assert data["configuration"]["valid"] is True
            assert data["configuration"]["errors"] == []
            assert data["configuration"]["warnings"] == []
            
            # JWT health
            assert "jwt" in data
            assert data["jwt"]["algorithm"] == "RS256"

    def test_detailed_health_check_unhealthy_config(self, client: TestClient):
        """Test detailed health check with invalid configuration."""
        mock_config_validation = {
            "config_valid": False,
            "errors": ["Missing JWT key", "Invalid database URL"],
            "warnings": ["Debug mode in production"]
        }
        
        with patch('app.repositories.base.test_database_connection', return_value=True), \
             patch('app.repositories.base.get_database_info', return_value={"database": "test"}), \
             patch('app.core.config.settings.validate_setup', return_value=mock_config_validation):
            
            response = client.get("/healthz/detailed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["configuration"]["valid"] is False
            assert len(data["configuration"]["errors"]) == 2
            assert len(data["configuration"]["warnings"]) == 1

    def test_detailed_health_check_unhealthy_database(self, client: TestClient):
        """Test detailed health check with unhealthy database."""
        mock_config_validation = {
            "config_valid": True,
            "errors": [],
            "warnings": []
        }
        
        with patch('app.repositories.base.test_database_connection', return_value=False), \
             patch('app.core.config.settings.validate_setup', return_value=mock_config_validation):
            
            response = client.get("/healthz/detailed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"]["connected"] is False
            assert data["database"]["info"]["error"] == "not connected"

    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client: AsyncClient):
        """Test health check with async client."""
        with patch('app.repositories.base.test_database_connection', new_callable=AsyncMock, return_value=True), \
             patch('app.repositories.base.get_database_info', new_callable=AsyncMock, return_value={
                 "database": "test_lorebound",
                 "active_connections": 3
             }):
            
            response = await async_client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"

    def test_metrics_endpoint(self, client: TestClient):
        """Test metrics endpoint placeholder."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert data["metrics"] == "placeholder"

    def test_health_endpoints_cors(self, client: TestClient):
        """Test CORS headers on health endpoints."""
        response = client.options("/healthz")
        assert response.status_code == 200
        
        response = client.options("/healthz/detailed")
        assert response.status_code == 200

    def test_health_check_with_environment_variables(self, client: TestClient):
        """Test health check reflects correct environment."""
        with patch('app.repositories.base.test_database_connection', return_value=True), \
             patch('app.core.config.settings.app_env', "test"):
            
            response = client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["environment"] == "test"


class TestHealthPerformance:
    """Test health check performance and reliability."""

    @pytest.mark.asyncio
    async def test_health_check_timeout_handling(self, async_client: AsyncClient):
        """Test health check handles database timeouts gracefully."""
        async def slow_db_check():
            # Simulate slow database response
            import asyncio
            await asyncio.sleep(0.1)
            return False
        
        with patch('app.repositories.base.test_database_connection', side_effect=slow_db_check):
            response = await async_client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"

    def test_health_check_exception_handling(self, client: TestClient):
        """Test health check handles unexpected exceptions."""
        with patch('app.repositories.base.test_database_connection', side_effect=Exception("Unexpected error")):
            response = client.get("/healthz")
            
            # Should still return 200 but mark as unhealthy
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"

    def test_concurrent_health_checks(self, client: TestClient):
        """Test multiple concurrent health check requests."""
        import threading
        results = []
        
        def make_request():
            with patch('app.repositories.base.test_database_connection', return_value=True):
                response = client.get("/healthz")
                results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert all(status == 200 for status in results)
        assert len(results) == 5
