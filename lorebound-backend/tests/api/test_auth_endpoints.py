"""Tests for authentication API endpoints."""

import pytest
import time
from httpx import AsyncClient
from fastapi import status

# Store current time for unique test data
pytest.current_time = int(time.time())


@pytest.mark.api
@pytest.mark.auth
class TestAuthEndpoints:
    """Test authentication API endpoints."""

    @pytest.mark.integration
    async def test_register_endpoint_success(self, async_client: AsyncClient):
        """Test successful user registration."""
        response = await async_client.post(
            "/v1/auth/register",
            json={
                "email": f"test_{pytest.current_time}@example.com",
                "password": "TestPassword123!",
                "handle": f"TestPlayer{pytest.current_time}"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "tokens" in data
        assert "user" in data
        assert data["tokens"]["access_token"] is not None

    @pytest.mark.integration
    async def test_register_endpoint_validation_error(self, async_client: AsyncClient):
        """Test registration with validation errors."""
        # Password too short
        response = await async_client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "handle": "TestPlayer"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert "Password must be at least" in data["detail"]

    @pytest.mark.integration
    async def test_register_endpoint_username_too_long(self, async_client: AsyncClient):
        """Test registration with username exceeding limit."""
        response = await async_client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
                "handle": "a" * 16  # Exceeds 15 character limit
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "Username must be no more than 15" in data["detail"]

    @pytest.mark.integration
    async def test_login_endpoint_success(self, async_client: AsyncClient, test_user, sample_user_data):
        """Test successful login."""
        response = await async_client.post(
            "/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tokens" in data
        assert "user" in data

    @pytest.mark.integration
    async def test_login_endpoint_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        response = await async_client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_get_current_user_endpoint(self, async_client: AsyncClient, test_user, auth_token):
        """Test getting current user info."""
        response = await async_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == str(test_user.id)

