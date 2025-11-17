"""Alternative authentication schemas without EmailStr dependency."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from ..domain.enums import UserStatus
from .email_validation import email_validator_func


class UserRegisterRequestAlt(BaseModel):
    """User registration request schema (alternative without EmailStr)."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=25, description="User password")
    handle: str = Field(..., min_length=3, max_length=15, description="User display name")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        return email_validator_func(v)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "player@example.com",
                "password": "SecurePassword123!",
                "handle": "AwesomePlayer"
            }
        }
    )


class UserLoginRequestAlt(BaseModel):
    """User login request schema (alternative without EmailStr)."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        return email_validator_func(v)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "player@example.com",
                "password": "SecurePassword123!"
            }
        }
    )


class AppleSignInRequestAlt(BaseModel):
    """Apple Sign-In request schema (alternative)."""
    identity_token: str = Field(..., description="Apple identity token")
    handle: Optional[str] = Field(None, min_length=3, max_length=15, description="User display name for new users")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "handle": "ApplePlayer"
            }
        }
    )


class TokenRefreshRequestAlt(BaseModel):
    """Token refresh request schema (alternative)."""
    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class TokenResponseAlt(BaseModel):
    """Authentication token response schema (alternative)."""
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


class UserResponseAlt(BaseModel):
    """User information response schema (alternative)."""
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


class AuthResponseAlt(BaseModel):
    """Complete authentication response schema (alternative)."""
    tokens: TokenResponseAlt = Field(..., description="Authentication tokens")
    user: UserResponseAlt = Field(..., description="User information")

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
