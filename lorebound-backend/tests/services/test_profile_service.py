"""Tests for ProfileService."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from app.services.profile_service import ProfileService
from app.services.exceptions import ProfileNotFoundError, HandleAlreadyExistsError
from app.domain.models import Profile


@pytest.mark.service
class TestProfileService:
    """Test ProfileService functionality."""

    @pytest.fixture
    def profile_service(self):
        """Create ProfileService instance."""
        return ProfileService()

    @pytest.mark.unit
    async def test_get_user_profile_success(self, profile_service, db_session, test_user, test_profile):
        """Test successful profile retrieval."""
        user_repo = Mock()
        user_repo.get_profile_by_user_id = AsyncMock(return_value=test_profile)
        
        with patch('app.services.profile_service.UserRepository', return_value=user_repo):
            result = await profile_service.get_user_profile(test_user.id, db_session)
            
            assert result is not None
            assert result.user_id == test_user.id
            assert result.handle == "TestPlayer"

    @pytest.mark.unit
    async def test_get_user_profile_not_found(self, profile_service, db_session, test_user):
        """Test profile retrieval when profile doesn't exist."""
        user_repo = Mock()
        user_repo.get_profile_by_user_id = AsyncMock(return_value=None)
        
        with patch('app.services.profile_service.UserRepository', return_value=user_repo):
            with pytest.raises(ProfileNotFoundError):
                await profile_service.get_user_profile(test_user.id, db_session)

    @pytest.mark.unit
    async def test_update_profile_handle(self, profile_service, db_session, test_user, test_profile):
        """Test updating profile handle."""
        user_repo = Mock()
        inventory_repo = Mock()
        user_repo.get_profile_by_user_id = AsyncMock(return_value=test_profile)
        user_repo.get_profile_by_handle = AsyncMock(return_value=None)
        user_repo.update_profile = AsyncMock(return_value=test_profile)
        
        with patch('app.services.profile_service.UserRepository', return_value=user_repo), \
             patch('app.services.profile_service.InventoryRepository', return_value=inventory_repo):
            result = await profile_service.update_user_profile(
                user_id=test_user.id,
                handle="NewHandle",
                session=db_session
            )
            
            assert result is not None

    @pytest.mark.unit
    async def test_update_profile_handle_exists(self, profile_service, db_session, test_user, test_profile):
        """Test updating profile with existing handle."""
        user_repo = Mock()
        inventory_repo = Mock()
        existing_profile = Mock(user_id=uuid4())
        user_repo.get_profile_by_user_id = AsyncMock(return_value=test_profile)
        user_repo.get_profile_by_handle = AsyncMock(return_value=existing_profile)
        
        with patch('app.services.profile_service.UserRepository', return_value=user_repo), \
             patch('app.services.profile_service.InventoryRepository', return_value=inventory_repo):
            with pytest.raises(HandleAlreadyExistsError):
                await profile_service.update_user_profile(
                    user_id=test_user.id,
                    handle="ExistingHandle",
                    session=db_session
                )

