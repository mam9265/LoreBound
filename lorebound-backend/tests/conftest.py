"""Pytest configuration and shared fixtures for the test suite."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.domain.models import Base, User, Profile
from app.domain.enums import UserStatus
from app.core.security import get_password_hash


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.app_env = "test"
    settings.debug = True
    settings.database_url = TEST_DATABASE_URL
    settings.redis_url = "redis://localhost:6379/1"
    settings.jwt_algorithm = "RS256"
    settings.jwt_private_key = b"test_private_key"
    settings.jwt_public_key = b"test_public_key"
    settings.jwt_access_token_expire_minutes = 15
    settings.jwt_refresh_token_expire_days = 7
    settings.cors_origins = ["http://localhost:3000"]
    return settings


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "handle": "TestPlayer"
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create a test user in the database."""
    user = User(
        id=uuid4(),
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_profile(db_session: AsyncSession, test_user: User) -> Profile:
    """Create a test profile for a user."""
    profile = Profile(
        user_id=test_user.id,
        handle="TestPlayer",
        level=1,
        xp=0,
        avatar_layers={}
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.delete_pattern = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_httpx_client():
    """Create a mock HTTP client for external API calls."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
async def async_client(test_engine, mock_settings):
    """Create async HTTP client for API testing."""
    from httpx import AsyncClient
    from app.main import create_app
    
    app = create_app()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_token(test_user, mock_settings):
    """Create an authentication token for testing."""
    from app.core.security import create_access_token
    
    token = create_access_token(
        subject=str(test_user.id),
        user_id=test_user.id
    )
    return token


@pytest.fixture
async def test_dungeon(db_session: AsyncSession):
    """Create a test dungeon."""
    from app.domain.models import Dungeon
    from app.domain.enums import DungeonCategory
    
    dungeon = Dungeon(
        id=uuid4(),
        title="Test Dungeon",
        category=DungeonCategory.GENERAL_KNOWLEDGE,
        modifiers={},
        content_version=1
    )
    db_session.add(dungeon)
    await db_session.commit()
    await db_session.refresh(dungeon)
    return dungeon


# Markers for test categorization
pytest_plugins = []

