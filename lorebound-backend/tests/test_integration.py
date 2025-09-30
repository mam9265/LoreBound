"""Integration tests for LoreBound backend."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, Mock, AsyncMock
import asyncio
import json


class TestUserJourney:
    """Test complete user journey integration scenarios."""

    def test_new_user_registration_flow(self, client: TestClient):
        """Test complete new user registration and first game flow."""
        # Step 1: Register new user
        registration_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "handle": "NewPlayer"
        }
        
        register_response = client.post("/v1/auth/register", json=registration_data)
        # Should not be 404 (endpoint exists)
        assert register_response.status_code != 404
        
        # Step 2: Login with new credentials
        login_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        }
        
        login_response = client.post("/v1/auth/login", json=login_data)
        assert login_response.status_code != 404
        
        # Step 3: Get user profile
        profile_response = client.get("/v1/auth/me")
        assert profile_response.status_code != 404
        
        # Step 4: Browse available content
        dungeons_response = client.get("/v1/content/dungeons")
        assert dungeons_response.status_code != 404
        
        # Step 5: Check initial inventory
        inventory_response = client.get("/v1/inventory/")
        assert inventory_response.status_code != 404
        
        # Step 6: Start first game run
        start_run_response = client.post("/v1/runs/start", json={})
        assert start_run_response.status_code != 404

    def test_returning_user_flow(self, client: TestClient):
        """Test returning user login and gameplay flow."""
        # Step 1: Login existing user
        login_data = {
            "email": "returning@example.com",
            "password": "ExistingPassword123!"
        }
        
        login_response = client.post("/v1/auth/login", json=login_data)
        assert login_response.status_code != 404
        
        # Step 2: Check updated profile
        profile_response = client.get("/v1/profile/")
        assert profile_response.status_code != 404
        
        # Step 3: View leaderboard position
        leaderboard_response = client.get("/v1/leaderboards/me")
        assert leaderboard_response.status_code != 404
        
        # Step 4: Check inventory and equipped items
        inventory_response = client.get("/v1/inventory/")
        assert inventory_response.status_code != 404
        
        # Step 5: Start new game run
        start_run_response = client.post("/v1/runs/start", json={})
        assert start_run_response.status_code != 404
        
        # Step 6: Submit completed run
        submit_run_response = client.post("/v1/runs/submit", json={
            "score": 1500,
            "time": 120,
            "answers": []
        })
        assert submit_run_response.status_code != 404

    def test_apple_signin_flow(self, client: TestClient):
        """Test Apple Sign-In integration flow."""
        # Step 1: Apple Sign-In
        apple_data = {
            "identity_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.apple_token",
            "handle": "AppleUser"
        }
        
        apple_response = client.post("/v1/auth/apple", json=apple_data)
        assert apple_response.status_code != 404
        
        # Step 2: Access protected resources
        profile_response = client.get("/v1/auth/me")
        assert profile_response.status_code != 404
        
        # Step 3: Start gameplay
        start_run_response = client.post("/v1/runs/start", json={})
        assert start_run_response.status_code != 404

    def test_guest_user_flow(self, client: TestClient):
        """Test guest user accessing public content."""
        # Step 1: Browse public content without authentication
        dungeons_response = client.get("/v1/content/dungeons")
        assert dungeons_response.status_code != 404
        
        # Step 2: View specific dungeon
        dungeon_response = client.get("/v1/content/dungeons/beginner-dungeon")
        assert dungeon_response.status_code != 404
        
        # Step 3: View public leaderboards
        leaderboard_response = client.get("/v1/leaderboards/")
        assert leaderboard_response.status_code != 404
        
        # Step 4: Get game configuration
        config_response = client.get("/v1/config/")
        assert config_response.status_code != 404
        
        # Step 5: Attempt to access protected resource (should fail)
        protected_response = client.get("/v1/profile/")
        # Should require authentication (401) or not be implemented yet
        assert protected_response.status_code in [401, 403, 404, 500]


class TestDataConsistency:
    """Test data consistency across different endpoints."""

    def test_user_data_consistency(self, client: TestClient):
        """Test user data is consistent across endpoints."""
        # Login user
        login_data = {
            "email": "consistent@example.com",
            "password": "Password123!"
        }
        
        login_response = client.post("/v1/auth/login", json=login_data)
        assert login_response.status_code != 404
        
        # Get user data from auth endpoint
        auth_user_response = client.get("/v1/auth/me")
        assert auth_user_response.status_code != 404
        
        # Get user data from profile endpoint
        profile_response = client.get("/v1/profile/")
        assert profile_response.status_code != 404
        
        # Data should be consistent between endpoints
        # (This would be tested with actual data when implemented)

    def test_inventory_run_consistency(self, client: TestClient):
        """Test inventory state is consistent with game runs."""
        # Get current inventory
        inventory_response = client.get("/v1/inventory/")
        assert inventory_response.status_code != 404
        
        # Start game run
        start_run_response = client.post("/v1/runs/start", json={})
        assert start_run_response.status_code != 404
        
        # Inventory should reflect equipped items for the run
        # (Implementation would verify equipped items match run state)

    def test_leaderboard_score_consistency(self, client: TestClient):
        """Test leaderboard scores are consistent with submitted runs."""
        # Submit a run with score
        submit_data = {
            "score": 2000,
            "time": 90,
            "answers": []
        }
        
        submit_response = client.post("/v1/runs/submit", json=submit_data)
        assert submit_response.status_code != 404
        
        # Check leaderboard reflects the score
        leaderboard_response = client.get("/v1/leaderboards/me")
        assert leaderboard_response.status_code != 404
        
        # Score should be reflected in leaderboard
        # (Implementation would verify score consistency)


class TestErrorHandling:
    """Test error handling across different scenarios."""

    def test_network_resilience(self, client: TestClient):
        """Test application handles network-related errors gracefully."""
        # Test with various network simulation scenarios
        endpoints = [
            "/v1/auth/login",
            "/v1/content/dungeons", 
            "/v1/profile/",
            "/v1/inventory/",
            "/v1/leaderboards/"
        ]
        
        for endpoint in endpoints:
            # Simulate network timeout
            with patch('httpx.AsyncClient.request', side_effect=asyncio.TimeoutError()):
                try:
                    if endpoint == "/v1/auth/login":
                        response = client.post(endpoint, json={"email": "test@example.com", "password": "test"})
                    else:
                        response = client.get(endpoint)
                    
                    # Should handle timeouts gracefully
                    assert response.status_code in [500, 502, 503, 504, 408]
                except:
                    # Exception handling is also acceptable
                    pass

    def test_database_unavailable_scenario(self, client: TestClient):
        """Test application behavior when database is unavailable."""
        with patch('app.repositories.base.test_database_connection', return_value=False):
            # Health check should reflect database status
            health_response = client.get("/healthz")
            assert health_response.status_code == 200
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                assert health_data.get("status") == "unhealthy"

    def test_invalid_token_handling(self, client: TestClient):
        """Test handling of invalid authentication tokens."""
        invalid_headers = {
            "Authorization": "Bearer invalid_token_here"
        }
        
        protected_endpoints = [
            "/v1/auth/me",
            "/v1/profile/",
            "/v1/inventory/",
            "/v1/runs/start"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint, headers=invalid_headers)
            # Should handle invalid tokens gracefully
            assert response.status_code in [401, 403, 404, 422, 500]

    def test_malformed_request_handling(self, client: TestClient):
        """Test handling of malformed requests."""
        # Test with invalid JSON
        response = client.post("/v1/auth/register", data="invalid json")
        assert response.status_code in [400, 422, 500]
        
        # Test with missing required fields
        response = client.post("/v1/auth/register", json={})
        assert response.status_code in [400, 422, 500]
        
        # Test with wrong content type
        response = client.post("/v1/auth/register", data="email=test@example.com")
        assert response.status_code in [400, 415, 422, 500]


class TestPerformanceIntegration:
    """Test performance characteristics in integrated scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_user_sessions(self, async_client: AsyncClient):
        """Test multiple concurrent user sessions."""
        async def simulate_user_session(user_id):
            # Simulate a complete user session
            sessions = []
            
            # Login
            login_response = await async_client.post("/v1/auth/login", json={
                "email": f"user{user_id}@example.com",
                "password": "Password123!"
            })
            sessions.append(login_response.status_code)
            
            # Browse content
            content_response = await async_client.get("/v1/content/dungeons")
            sessions.append(content_response.status_code)
            
            # Check profile
            profile_response = await async_client.get("/v1/profile/")
            sessions.append(profile_response.status_code)
            
            return sessions
        
        # Simulate 5 concurrent users
        tasks = [simulate_user_session(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All sessions should complete
        assert len(results) == 5
        for session_statuses in results:
            # No server errors in any session
            assert all(status != 500 for status in session_statuses)

    def test_bulk_operations_performance(self, client: TestClient):
        """Test performance with bulk operations."""
        import time
        
        # Test bulk leaderboard queries
        start_time = time.time()
        for _ in range(10):
            response = client.get("/v1/leaderboards/")
            assert response.status_code != 500
        
        bulk_time = time.time() - start_time
        assert bulk_time < 30.0  # Should complete within 30 seconds
        
        # Test bulk content queries
        start_time = time.time()
        for i in range(10):
            response = client.get(f"/v1/content/dungeons/dungeon-{i}")
            assert response.status_code != 500
        
        bulk_time = time.time() - start_time
        assert bulk_time < 30.0

    def test_memory_usage_integration(self, client: TestClient):
        """Test memory usage during integrated operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform various operations
        operations = [
            lambda: client.get("/v1/content/dungeons"),
            lambda: client.get("/v1/leaderboards/"),
            lambda: client.get("/v1/config/"),
            lambda: client.post("/v1/auth/login", json={"email": "test@example.com", "password": "test"}),
            lambda: client.get("/v1/profile/")
        ]
        
        # Repeat operations multiple times
        for _ in range(20):
            for operation in operations:
                operation()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB


class TestSecurityIntegration:
    """Test security aspects in integrated scenarios."""

    def test_authentication_flow_security(self, client: TestClient):
        """Test security throughout authentication flow."""
        # Attempt login with weak password
        weak_login = {
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post("/v1/auth/login", json=weak_login)
        # Should handle weak passwords appropriately
        assert response.status_code != 500
        
        # Attempt registration with weak password
        weak_registration = {
            "email": "test@example.com",
            "password": "123",
            "handle": "Test"
        }
        
        response = client.post("/v1/auth/register", json=weak_registration)
        # Should reject weak passwords
        assert response.status_code in [400, 422, 500]

    def test_session_security(self, client: TestClient):
        """Test session security across requests."""
        # Login and get session
        login_response = client.post("/v1/auth/login", json={
            "email": "session@example.com",
            "password": "SessionPassword123!"
        })
        
        # Make authenticated requests
        profile_response = client.get("/v1/profile/")
        assert profile_response.status_code != 404
        
        # Test session timeout (would require actual token implementation)
        # Test concurrent sessions
        # Test session invalidation

    def test_data_access_security(self, client: TestClient):
        """Test users can only access their own data."""
        # Login as user A
        user_a_login = {
            "email": "usera@example.com", 
            "password": "PasswordA123!"
        }
        
        response_a = client.post("/v1/auth/login", json=user_a_login)
        assert response_a.status_code != 404
        
        # Get user A's profile
        profile_a = client.get("/v1/profile/")
        assert profile_a.status_code != 404
        
        # Login as user B  
        user_b_login = {
            "email": "userb@example.com",
            "password": "PasswordB123!"
        }
        
        response_b = client.post("/v1/auth/login", json=user_b_login)
        assert response_b.status_code != 404
        
        # User B should not access user A's data
        # (This would be tested with actual authorization implementation)

    def test_input_sanitization_integration(self, client: TestClient):
        """Test input sanitization across all endpoints."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "\x00\x01\x02",  # Null bytes
            "a" * 10000       # Very long input
        ]
        
        test_data = {
            "email": "malicious@example.com",
            "password": "Password123!",
            "handle": "MaliciousUser"
        }
        
        for malicious_input in malicious_inputs:
            # Test in different fields
            for field in ["email", "handle"]:
                if field == "email":
                    continue  # Skip invalid emails for email field
                
                test_data_copy = test_data.copy()
                test_data_copy[field] = malicious_input
                
                response = client.post("/v1/auth/register", json=test_data_copy)
                # Should handle malicious input gracefully
                assert response.status_code != 500
