"""Authentication schemas for request/response validation."""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from ..domain.enums import UserStatus

# Try to import EmailStr, fall back to custom validation if not available
try:
    from pydantic import EmailStr
    EMAIL_STR_AVAILABLE = True
except ImportError:
    EMAIL_STR_AVAILABLE = False
    EmailStr = str  # Fallback to string type

# Import custom email validation
from .email_validation import email_validator_func


class UserRegisterRequest(BaseModel):
    """User registration request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    handle: str = Field(..., min_length=3, max_length=50, description="User display name")

    @field_validator('email')
    @classmethod
    def validate_email_fallback(cls, v):
        """Validate email with fallback if EmailStr validation fails."""
        if not EMAIL_STR_AVAILABLE:
            return email_validator_func(v)
        # Normalize email to lowercase
        return v.lower().strip() if isinstance(v, str) else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "player@example.com",
                "password": "SecurePassword123!",
                "handle": "AwesomePlayer"
            }
        }
    )


class UserLoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator('email')
    @classmethod
    def validate_email_fallback(cls, v):
        """Validate email with fallback if EmailStr validation fails."""
        if not EMAIL_STR_AVAILABLE:
            return email_validator_func(v)
        # Normalize email to lowercase
        return v.lower().strip() if isinstance(v, str) else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "player@example.com",
                "password": "SecurePassword123!"
            }
        }
    )


class AppleSignInRequest(BaseModel):
    """Apple Sign-In request schema."""
    identity_token: str = Field(..., description="Apple identity token")
    handle: Optional[str] = Field(None, min_length=3, max_length=50, description="User display name for new users")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "handle": "ApplePlayer"
            }
        }
    )


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class TokenResponse(BaseModel):
    """Authentication token response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    )


class UserResponse(BaseModel):
    """User information response schema."""
    id: UUID = Field(..., description="User unique identifier")
    email: Optional[str] = Field(None, description="User email address")
    apple_sub: Optional[str] = Field(None, description="Apple subject identifier")
    status: UserStatus = Field(..., description="User account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "player@example.com",
                "apple_sub": None,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class AuthResponse(BaseModel):
    """Complete authentication response schema."""
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tokens": {
                    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900
                },
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "player@example.com",
                    "apple_sub": None,
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_login_at": "2024-01-01T12:00:00Z"
                }
            }
        }
    )
