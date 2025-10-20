"""Custom exceptions for service layer."""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class AuthenticationError(ServiceError):
    """Raised when authentication operations fail."""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Raised when attempting to create a user that already exists."""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when a user cannot be found."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when provided credentials are invalid."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""
    pass


class AppleSignInError(AuthenticationError):
    """Raised when Apple Sign-In operations fail."""
    pass


class ContentError(ServiceError):
    """Base exception for content service errors."""
    pass


class QuestionNotFoundError(ContentError):
    """Raised when questions cannot be found or fetched."""
    pass


class DungeonNotFoundError(ContentError):
    """Raised when a dungeon cannot be found."""
    pass


class DailyChallengeError(ContentError):
    """Raised when daily challenge operations fail."""
    pass


class ExternalAPIError(ServiceError):
    """Raised when external API calls fail."""
    pass


class TriviaAPIError(ExternalAPIError):
    """Raised when trivia API calls fail."""
    pass


class RunServiceError(ServiceError):
    """Base exception for run service errors."""
    pass


class InvalidRunDataError(RunServiceError):
    """Raised when run data is invalid or corrupted."""
    pass


class AntiCheatViolationError(RunServiceError):
    """Raised when anti-cheat validation fails."""
    pass


class ScoreCalculationError(RunServiceError):
    """Raised when score calculation fails."""
    pass


class InventoryError(ServiceError):
    """Base exception for inventory service errors."""
    pass


class ItemNotFoundError(InventoryError):
    """Raised when an item cannot be found."""
    pass


class InsufficientItemsError(InventoryError):
    """Raised when user doesn't have enough items."""
    pass


class LeaderboardError(ServiceError):
    """Base exception for leaderboard service errors."""
    pass


class RankingCalculationError(LeaderboardError):
    """Raised when ranking calculation fails."""
    pass
