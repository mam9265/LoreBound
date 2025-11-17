"""Tests for ContentService."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch

from app.services.content_service import ContentService
from app.services.exceptions import DungeonNotFoundError, ContentError


@pytest.mark.service
class TestContentService:
    """Test ContentService functionality."""

    @pytest.fixture
    def content_service(self, mock_settings):
        """Create ContentService instance."""
        content_repo = Mock()
        trivia_client = Mock()
        return ContentService(content_repo, trivia_client, mock_settings)

    @pytest.mark.unit
    async def test_get_available_dungeons_success(self, content_service, db_session):
        """Test successful dungeon retrieval."""
        mock_dungeons = [Mock(id=uuid4(), title="Test Dungeon")]
        content_service.content_repo.get_all_dungeons = AsyncMock(return_value=mock_dungeons)
        
        result = await content_service.get_available_dungeons(db_session)
        
        assert result is not None
        assert len(result) > 0

    @pytest.mark.unit
    async def test_get_dungeon_by_id_success(self, content_service, db_session):
        """Test successful dungeon retrieval by ID."""
        dungeon_id = uuid4()
        mock_dungeon = Mock(id=dungeon_id, title="Test Dungeon")
        content_service.content_repo.get_dungeon_by_id = AsyncMock(return_value=mock_dungeon)
        
        result = await content_service.get_dungeon_by_id(dungeon_id, db_session)
        
        assert result is not None
        assert result.id == dungeon_id

    @pytest.mark.unit
    async def test_get_dungeon_by_id_not_found(self, content_service, db_session):
        """Test dungeon retrieval with non-existent ID."""
        dungeon_id = uuid4()
        content_service.content_repo.get_dungeon_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(DungeonNotFoundError):
            await content_service.get_dungeon_by_id(dungeon_id, db_session)

    @pytest.mark.unit
    async def test_get_questions_for_dungeon(self, content_service, db_session, test_user):
        """Test question retrieval for dungeon."""
        dungeon_id = uuid4()
        mock_questions = [Mock(id=uuid4(), prompt="Test question")]
        content_service.content_repo.get_questions_for_dungeon = AsyncMock(return_value=mock_questions)
        
        result = await content_service.get_questions_for_dungeon(
            dungeon_id=dungeon_id,
            floor=1,
            count=5,
            user_id=test_user.id,
            session=db_session
        )
        
        assert result is not None
        assert len(result) > 0

