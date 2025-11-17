"""Tests for AuthenticationService."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch

from app.services.auth_service import AuthenticationService
from app.services.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.domain.enums import UserStatus


@pytest.mark.service
@pytest.mark.auth
class TestAuthenticationService:
    """Test AuthenticationService functionality."""

    @pytest.fixture
    def auth_service(self, mock_settings):
        """Create AuthenticationService instance."""
        user_repo = Mock()
        apple_service = Mock()
        return AuthenticationService(user_repo, apple_service, mock_settings)

    @pytest.mark.unit
    async def test_register_user_success(self, auth_service, db_session, sample_user_data):
        """Test successful user registration."""
        # Mock repository methods
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=None)
        auth_service.user_repo.get_profile_by_handle = AsyncMock(return_value=None)
        auth_service.user_repo.create_user = AsyncMock(return_value=Mock(id=uuid4()))
        auth_service.user_repo.create_profile = AsyncMock(return_value=Mock())
        auth_service.user_repo.add_base_items_to_user = AsyncMock()
        
        # Mock token generation
        auth_service._generate_token_pair = Mock(return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 900
        })
        
        registration_data = UserRegisterRequest(**sample_user_data)
        result = await auth_service.register_user(registration_data, db_session)
        
        assert result is not None
        assert result.user is not None
        assert result.tokens is not None

    @pytest.mark.unit
    async def test_register_user_email_exists(self, auth_service, db_session, sample_user_data):
        """Test registration with existing email."""
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=Mock(id=uuid4()))
        
        registration_data = UserRegisterRequest(**sample_user_data)
        
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(registration_data, db_session)

    @pytest.mark.unit
    async def test_register_user_handle_exists(self, auth_service, db_session, sample_user_data):
        """Test registration with existing handle."""
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=None)
        auth_service.user_repo.get_profile_by_handle = AsyncMock(return_value=Mock())
        
        registration_data = UserRegisterRequest(**sample_user_data)
        
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(registration_data, db_session)

    @pytest.mark.unit
    async def test_login_user_success(self, auth_service, db_session, test_user, sample_user_data):
        """Test successful user login."""
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=test_user)
        auth_service.user_repo.update_user_login_time = AsyncMock()
        auth_service._generate_token_pair = Mock(return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 900
        })
        
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        result = await auth_service.login_user(login_data, db_session)
        
        assert result is not None
        assert result.user is not None
        assert result.tokens is not None

    @pytest.mark.unit
    async def test_login_user_invalid_email(self, auth_service, db_session, sample_user_data):
        """Test login with non-existent email."""
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=None)
        
        login_data = UserLoginRequest(
            email="nonexistent@example.com",
            password=sample_user_data["password"]
        )
        
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(login_data, db_session)

    @pytest.mark.unit
    async def test_login_user_invalid_password(self, auth_service, db_session, test_user, sample_user_data):
        """Test login with incorrect password."""
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=test_user)
        
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password="WrongPassword123!"
        )
        
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(login_data, db_session)

    @pytest.mark.unit
    async def test_login_user_inactive(self, auth_service, db_session, test_user, sample_user_data):
        """Test login with inactive user account."""
        test_user.status = UserStatus.SUSPENDED
        auth_service.user_repo.get_user_by_email = AsyncMock(return_value=test_user)
        
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(login_data, db_session)

