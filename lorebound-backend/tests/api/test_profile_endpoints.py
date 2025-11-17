"""Tests for profile API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.api
class TestProfileEndpoints:
    """Test profile API endpoints."""

    @pytest.mark.integration
    async def test_get_profile_endpoint(self, async_client: AsyncClient, auth_token, test_profile):
        """Test getting user profile."""
        response = await async_client.get(
            "/v1/profile/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user_id" in data
        assert "handle" in data
        assert "level" in data

    @pytest.mark.integration
    async def test_update_profile_endpoint(self, async_client: AsyncClient, auth_token):
        """Test updating user profile."""
        response = await async_client.put(
            "/v1/profile/",
            json={
                "handle": "NewHandle123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["handle"] == "NewHandle123"

    @pytest.mark.integration
    async def test_update_profile_handle_too_long(self, async_client: AsyncClient, auth_token):
        """Test updating profile with handle exceeding limit."""
        response = await async_client.put(
            "/v1/profile/",
            json={
                "handle": "a" * 16  # Exceeds 15 character limit
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "Username must be no more than 15" in data["detail"]

