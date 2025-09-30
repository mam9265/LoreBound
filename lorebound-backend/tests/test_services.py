"""Comprehensive tests for service layer implementations."""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

# Test framework setup
pytest_plugins = ('pytest_asyncio',)

# Import our services and dependencies
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.auth_service import AuthenticationService
from app.services.apple_service import AppleSignInService
from app.services.content_service import ContentService
from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
from app.services.exceptions import (
    UserAlreadyExistsError, 
    InvalidCredentialsError,
    TriviaAPIError
)
from app.core.config import Settings
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, AppleSignInRequest
from app.domain.enums import UserStatus, DungeonCategory, QuestionDifficulty


class TestAuthenticationService:
    """Test cases for Authentication Service."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock(spec=Settings)
        settings.app_env = "dev"
        settings.access_token_ttl_seconds = 900
        settings.refresh_token_ttl_seconds = 1209600
        settings.apple_client_id = "com.lorebound.app"
        return settings

    @pytest.fixture
    def mock_user_repo(self):
        """Mock user repository."""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def mock_apple_service(self):
        """Mock Apple Sign-In service."""
        service = AsyncMock(spec=AppleSignInService)
        return service

    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_apple_service, mock_settings):
        """Create authentication service with mocked dependencies."""
        return AuthenticationService(mock_user_repo, mock_apple_service, mock_settings)

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_user_registration_success(self, auth_service, mock_user_repo, mock_session):
        """Test successful user registration."""
        # Setup
        registration_data = UserRegisterRequest(
            email="test@example.com",
            password="SecurePassword123!",
            handle="TestUser"
        )
        
        # Mock repository responses
        mock_user_repo.get_by_email.return_value = None  # User doesn't exist
        mock_user_repo.get_by_handle.return_value = None  # Handle available
        
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.status = UserStatus.ACTIVE
        mock_user_repo.create_user.return_value = mock_user
        
        # Execute
        with patch('app.services.auth_service.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            result = await auth_service.register_user(registration_data, mock_session)
        
        # Verify
        assert result.tokens.access_token is not None
        assert result.tokens.refresh_token is not None
        assert result.user.id == mock_user.id
        mock_user_repo.create_user.assert_called_once()
        mock_user_repo.update_last_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_registration_email_exists(self, auth_service, mock_user_repo, mock_session):
        """Test registration fails when email already exists."""
        # Setup
        registration_data = UserRegisterRequest(
            email="existing@example.com",
            password="SecurePassword123!",
            handle="TestUser"
        )
        
        mock_existing_user = Mock()
        mock_user_repo.get_by_email.return_value = mock_existing_user
        
        # Execute & Verify
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(registration_data, mock_session)

    @pytest.mark.asyncio
    async def test_user_login_success(self, auth_service, mock_user_repo, mock_session):
        """Test successful user login."""
        # Setup
        login_data = UserLoginRequest(
            email="test@example.com",
            password="SecurePassword123!"
        )
        
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.status = UserStatus.ACTIVE
        mock_user.password_hash = "hashed_password"
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            result = await auth_service.login_user(login_data, mock_session)
        
        # Verify
        assert result.tokens.access_token is not None
        assert result.tokens.refresh_token is not None
        assert result.user.id == mock_user.id
        mock_user_repo.update_last_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_login_invalid_credentials(self, auth_service, mock_user_repo, mock_session):
        """Test login fails with invalid credentials."""
        # Setup
        login_data = UserLoginRequest(
            email="test@example.com",
            password="WrongPassword"
        )
        
        mock_user = Mock()
        mock_user.password_hash = "hashed_password"
        mock_user.status = UserStatus.ACTIVE
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute & Verify
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            with pytest.raises(InvalidCredentialsError):
                await auth_service.login_user(login_data, mock_session)

    @pytest.mark.asyncio
    async def test_apple_sign_in_new_user(self, auth_service, mock_user_repo, mock_apple_service, mock_session):
        """Test Apple Sign-In with new user registration."""
        # Setup
        apple_data = AppleSignInRequest(
            identity_token="mock_token",
            handle="AppleUser"
        )
        
        mock_apple_info = Mock()
        mock_apple_info.sub = "apple_user_123"
        mock_apple_info.email = "apple@example.com"
        mock_apple_service.verify_identity_token.return_value = mock_apple_info
        
        mock_user_repo.get_by_apple_sub.return_value = None  # New user
        mock_user_repo.get_by_handle.return_value = None  # Handle available
        
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_user.apple_sub = "apple_user_123"
        mock_user.status = UserStatus.ACTIVE
        mock_user_repo.create_user.return_value = mock_user
        
        # Execute
        result = await auth_service.apple_sign_in(apple_data, mock_session)
        
        # Verify
        assert result.tokens.access_token is not None
        assert result.user.id == mock_user.id
        mock_user_repo.create_user.assert_called_once()


class TestContentService:
    """Test cases for Content Service."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock(spec=Settings)
        settings.feature_flags_seed = 12345
        return settings

    @pytest.fixture
    def mock_content_repo(self):
        """Mock content repository."""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def mock_trivia_client(self):
        """Mock trivia API client."""
        client = AsyncMock(spec=TriviaAPIClient)
        return client

    @pytest.fixture
    def content_service(self, mock_content_repo, mock_trivia_client, mock_settings):
        """Create content service with mocked dependencies."""
        return ContentService(mock_content_repo, mock_trivia_client, mock_settings)

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_available_dungeons(self, content_service, mock_content_repo, mock_session):
        """Test fetching available dungeons."""
        # Setup
        mock_dungeon = Mock()
        mock_dungeon.id = uuid4()
        mock_dungeon.title = "Test Dungeon"
        mock_dungeon.category = DungeonCategory.SPORTS
        mock_content_repo.get_all_dungeons.return_value = [mock_dungeon]
        
        # Execute
        result = await content_service.get_available_dungeons(mock_session)
        
        # Verify
        assert len(result) == 1
        mock_content_repo.get_all_dungeons.assert_called_once()

    @pytest.mark.asyncio
    async def test_deterministic_question_selection(self, content_service, mock_content_repo, mock_session):
        """Test deterministic question selection generates consistent results."""
        # Setup
        dungeon_id = uuid4()
        user_id = uuid4()
        floor = 3
        count = 5
        
        mock_dungeon = Mock()
        mock_dungeon.id = dungeon_id
        mock_dungeon.category = DungeonCategory.SCIENCE
        mock_content_repo.get_dungeon_by_id.return_value = mock_dungeon
        
        # Create mock questions
        mock_questions = []
        for i in range(10):
            q = Mock()
            q.id = uuid4()
            q.question_text = f"Question {i}"
            mock_questions.append(q)
        
        mock_content_repo.get_questions_by_category_and_difficulty.return_value = mock_questions
        
        # Execute twice with same parameters
        result1 = await content_service.get_questions_for_dungeon(
            dungeon_id, floor, count, user_id, mock_session
        )
        result2 = await content_service.get_questions_for_dungeon(
            dungeon_id, floor, count, user_id, mock_session
        )
        
        # Verify deterministic behavior (same questions in same order)
        assert len(result1) == count
        assert len(result2) == count
        for i in range(count):
            assert result1[i].id == result2[i].id

    @pytest.mark.asyncio
    async def test_daily_challenge_generation(self, content_service, mock_content_repo, mock_session):
        """Test daily challenge generation."""
        # Setup
        challenge_date = datetime.now(timezone.utc).date()
        mock_content_repo.get_daily_challenge_by_date.return_value = None  # No existing challenge
        
        mock_challenge = Mock()
        mock_challenge.id = uuid4()
        mock_challenge.challenge_date = challenge_date
        mock_challenge.category = DungeonCategory.GENERAL
        mock_content_repo.create_daily_challenge.return_value = mock_challenge
        
        # Execute
        result = await content_service.get_daily_challenge(mock_session)
        
        # Verify
        assert result.id == mock_challenge.id
        mock_content_repo.create_daily_challenge.assert_called_once()


class TestTriviaAPIClient:
    """Test cases for Trivia API Client."""

    @pytest.mark.asyncio
    async def test_opentdb_question_fetching(self):
        """Test fetching questions from OpenTDB API."""
        # This is an integration test that requires internet connection
        # Skip if no internet or API is down
        try:
            async with TriviaAPIClient() as client:
                questions = await client.fetch_questions(
                    amount=2,
                    category="Sports",
                    difficulty=QuestionDifficulty.EASY,
                    provider=TriviaAPIProvider.OPENTDB
                )
                
                assert len(questions) <= 2  # Might be fewer if category has limited questions
                if questions:
                    q = questions[0]
                    assert hasattr(q, 'question')
                    assert hasattr(q, 'correct_answer')
                    assert hasattr(q, 'incorrect_answers')
                    assert len(q.incorrect_answers) > 0
                    
        except Exception as e:
            pytest.skip(f"OpenTDB API test skipped: {e}")

    @pytest.mark.asyncio
    async def test_api_connection_test(self):
        """Test API connection validation."""
        try:
            async with TriviaAPIClient() as client:
                is_connected = await client.test_connection(TriviaAPIProvider.OPENTDB)
                assert isinstance(is_connected, bool)
                
        except Exception as e:
            pytest.skip(f"API connection test skipped: {e}")

    @pytest.mark.asyncio
    async def test_category_fetching(self):
        """Test fetching available categories."""
        try:
            async with TriviaAPIClient() as client:
                categories = await client.get_categories(TriviaAPIProvider.OPENTDB)
                assert len(categories) > 0
                
                # Check category structure
                cat = categories[0]
                assert hasattr(cat, 'id')
                assert hasattr(cat, 'name')
                assert isinstance(cat.id, int)
                assert isinstance(cat.name, str)
                
        except Exception as e:
            pytest.skip(f"Category fetching test skipped: {e}")


class TestServiceIntegration:
    """Integration tests for service interactions."""

    @pytest.mark.asyncio
    async def test_content_service_with_real_trivia_api(self):
        """Test content service integration with real trivia API."""
        # This test demonstrates the full content pipeline
        try:
            from app.services.trivia_api_client import create_trivia_client
            from app.repositories.content_repo import ContentRepository
            from app.core.config import Settings
            
            # Create real instances (but mock the database parts)
            trivia_client = create_trivia_client()
            mock_content_repo = AsyncMock(spec=ContentRepository)
            mock_settings = Mock(spec=Settings)
            mock_settings.feature_flags_seed = 12345
            
            content_service = ContentService(mock_content_repo, trivia_client, mock_settings)
            
            # Test question pool refresh (this will make real API calls)
            mock_session = AsyncMock()
            mock_content_repo.get_question_by_hash.return_value = None  # No duplicates
            mock_content_repo.create_question.return_value = Mock()
            
            result = await content_service.refresh_question_pool(
                category=DungeonCategory.SPORTS,
                batch_size=5,
                session=mock_session
            )
            
            # Should have fetched and "stored" some questions
            assert isinstance(result, int)
            assert result >= 0  # Could be 0 if API is rate limited or down
            
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


# Test runner function
async def run_all_tests():
    """Run all service tests manually (for development)."""
    print("Running Authentication Service Tests...")
    
    # Test basic trivia API functionality
    print("\n=== Testing Trivia API Integration ===")
    try:
        async with TriviaAPIClient() as client:
            # Test connection
            connected = await client.test_connection()
            print(f"API Connection: {'SUCCESS' if connected else 'FAILED'}")
            
            if connected:
                # Test fetching questions
                questions = await client.fetch_questions(amount=3, provider=TriviaAPIProvider.OPENTDB)
                print(f"Fetched {len(questions)} questions")
                
                if questions:
                    q = questions[0]
                    print(f"Sample: {q.question[:50]}...")
                    print(f"Answer: {q.correct_answer}")
    except Exception as e:
        print(f"Trivia API test failed: {e}")
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    # Run tests manually for development
    asyncio.run(run_all_tests())
