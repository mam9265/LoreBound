"""User and profile schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import UserStatus


class ProfileResponse(BaseModel):
    """User profile response schema."""
    user_id: UUID = Field(..., description="User unique identifier")
    handle: str = Field(..., description="User display name")
    level: int = Field(..., description="User level")
    xp: int = Field(..., description="User experience points")
    avatar_layers: Dict[str, Any] = Field(default_factory=dict, description="Avatar customization data")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "handle": "AwesomePlayer",
                "level": 15,
                "xp": 12500,
                "avatar_layers": {
                    "skin": "fair",
                    "hair": "brown",
                    "eyes": "blue",
                    "outfit": "casual"
                }
            }
        }
    )


class ProfileUpdateRequest(BaseModel):
    """Profile update request schema."""
    handle: Optional[str] = Field(None, min_length=3, max_length=50, description="New display name")
    avatar_layers: Optional[Dict[str, Any]] = Field(None, description="Avatar customization data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "handle": "NewAwesomePlayer",
                "avatar_layers": {
                    "skin": "tan",
                    "hair": "black",
                    "eyes": "green",
                    "outfit": "formal"
                }
            }
        }
    )


class UserProfileResponse(BaseModel):
    """Complete user profile with user data."""
    user_id: UUID = Field(..., description="User unique identifier")
    email: Optional[str] = Field(None, description="User email address")
    status: UserStatus = Field(..., description="User account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    profile: ProfileResponse = Field(..., description="User profile data")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "player@example.com",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "profile": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "handle": "AwesomePlayer",
                    "level": 15,
                    "xp": 12500,
                    "avatar_layers": {
                        "skin": "fair",
                        "hair": "brown",
                        "eyes": "blue",
                        "outfit": "casual"
                    }
                }
            }
        }
    )
