"""Tests for content API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.api
class TestContentEndpoints:
    """Test content API endpoints."""

    @pytest.mark.integration
    async def test_get_dungeons_endpoint(self, async_client: AsyncClient, auth_token):
        """Test getting available dungeons."""
        response = await async_client.get(
            "/v1/content/dungeons",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.integration
    async def test_get_dungeon_details_endpoint(self, async_client: AsyncClient, auth_token, test_dungeon):
        """Test getting dungeon details."""
        response = await async_client.get(
            f"/v1/content/dungeons/{test_dungeon.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == str(test_dungeon.id)

    @pytest.mark.integration
    async def test_get_questions_endpoint(self, async_client: AsyncClient, auth_token, test_dungeon):
        """Test getting questions for a dungeon."""
        response = await async_client.get(
            f"/v1/content/dungeons/{test_dungeon.id}/questions",
            params={"floor": 1, "count": 5},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)

