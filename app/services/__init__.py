"""Services module for business logic layer."""

from .auth_service import AuthenticationService, get_auth_service
from .apple_service import AppleSignInService, get_apple_service
from .content_service import ContentService, get_content_service
from .trivia_api_client import TriviaAPIClient, create_trivia_client
from .exceptions import (
    ServiceError,
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    TokenExpiredError,
    AppleSignInError,
    ContentError,
    QuestionNotFoundError,
    DungeonNotFoundError,
    DailyChallengeError,
    ExternalAPIError,
    TriviaAPIError
)

__all__ = [
    # Services
    "AuthenticationService",
    "AppleSignInService", 
    "ContentService",
    "TriviaAPIClient",
    
    # Service factories
    "get_auth_service",
    "get_apple_service",
    "get_content_service",
    "create_trivia_client",
    
    # Exceptions
    "ServiceError",
    "AuthenticationError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "AppleSignInError",
    "ContentError",
    "QuestionNotFoundError",
    "DungeonNotFoundError",
    "DailyChallengeError",
    "ExternalAPIError",
    "TriviaAPIError",
]