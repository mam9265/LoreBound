"""Service layer dependency injection."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings, get_settings
from ..repositories.base import get_session
from ..repositories.user_repo import UserRepository
from ..repositories.content_repo import ContentRepository

from .auth_service import AuthenticationService
from .apple_service import AppleSignInService
from .content_service import ContentService
from .run_service import RunService
from .trivia_api_client import TriviaAPIClient, create_trivia_client


# Repository Dependencies
def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(session)


def get_content_repository(session: AsyncSession = Depends(get_session)) -> ContentRepository:
    """Get content repository instance."""
    return ContentRepository(session)


# Service Dependencies
def get_apple_service(settings: Settings = Depends(get_settings)) -> AppleSignInService:
    """Get Apple Sign-In service instance."""
    return AppleSignInService(settings)


def get_trivia_client() -> TriviaAPIClient:
    """Get trivia API client instance."""
    return create_trivia_client()


# Service factories that create services with session
async def get_auth_service_with_session(
    session: AsyncSession = Depends(get_session),
    apple_service: AppleSignInService = Depends(get_apple_service),
    settings: Settings = Depends(get_settings)
) -> tuple[AuthenticationService, AsyncSession]:
    """Get authentication service with database session."""
    user_repo = UserRepository(session)
    auth_service = AuthenticationService(user_repo, apple_service, settings)
    return auth_service, session


async def get_content_service_with_session(
    session: AsyncSession = Depends(get_session),
    trivia_client: TriviaAPIClient = Depends(get_trivia_client),
    settings: Settings = Depends(get_settings)
) -> tuple[ContentService, AsyncSession]:
    """Get content service with database session."""
    content_repo = ContentRepository(session)
    content_service = ContentService(content_repo, trivia_client, settings)
    return content_service, session


async def get_run_service_with_session(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings)
) -> tuple[RunService, AsyncSession]:
    """Get run service with database session."""
    from ..repositories.run_repo import RunRepository
    user_repo = UserRepository(session)
    run_repo = RunRepository(session)
    run_service = RunService(run_repo, user_repo, settings)
    return run_service, session
