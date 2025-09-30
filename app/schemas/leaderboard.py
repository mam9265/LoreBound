"""Leaderboard schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import LeaderboardScope


class LeaderboardEntryResponse(BaseModel):
    """Individual leaderboard entry schema."""
    rank: int = Field(..., description="Player rank on leaderboard")
    user_id: UUID = Field(..., description="User identifier")
    handle: str = Field(..., description="Player display name")
    score: int = Field(..., description="Player score")
    run_id: UUID = Field(..., description="Run identifier for this score")
    created_at: datetime = Field(..., description="Score timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rank": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "handle": "AwesomePlayer",
                "score": 25000,
                "run_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class LeaderboardRequest(BaseModel):
    """Leaderboard request query parameters."""
    scope: LeaderboardScope = Field(default=LeaderboardScope.TODAY, description="Leaderboard time scope")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of entries to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scope": "today",
                "limit": 50,
                "offset": 0
            }
        }
    )


class LeaderboardResponse(BaseModel):
    """Leaderboard response schema."""
    scope: LeaderboardScope = Field(..., description="Leaderboard time scope")
    period_key: str = Field(..., description="Period identifier (e.g., '2024-01-01', '2024-W01')")
    entries: List[LeaderboardEntryResponse] = Field(..., description="Leaderboard entries")
    total_count: int = Field(..., description="Total number of entries in this leaderboard")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scope": "today",
                "period_key": "2024-01-01",
                "entries": [
                    {
                        "rank": 1,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "handle": "AwesomePlayer",
                        "score": 25000,
                        "run_id": "123e4567-e89b-12d3-a456-426614174001",
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total_count": 1500,
                "updated_at": "2024-01-01T12:30:00Z"
            }
        }
    )


class UserRankRequest(BaseModel):
    """User rank request query parameters."""
    scope: LeaderboardScope = Field(default=LeaderboardScope.TODAY, description="Leaderboard time scope")
    neighbors: int = Field(default=5, ge=0, le=50, description="Number of neighbors to show above/below user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scope": "weekly",
                "neighbors": 3
            }
        }
    )


class UserRankResponse(BaseModel):
    """User rank response schema."""
    scope: LeaderboardScope = Field(..., description="Leaderboard time scope")
    period_key: str = Field(..., description="Period identifier")
    user_entry: Optional[LeaderboardEntryResponse] = Field(None, description="User's leaderboard entry")
    neighbors: List[LeaderboardEntryResponse] = Field(default_factory=list, description="Neighboring entries")
    total_count: int = Field(..., description="Total entries in leaderboard")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scope": "weekly",
                "period_key": "2024-W01",
                "user_entry": {
                    "rank": 42,
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "handle": "AwesomePlayer",
                    "score": 18500,
                    "run_id": "123e4567-e89b-12d3-a456-426614174001",
                    "created_at": "2024-01-01T12:00:00Z"
                },
                "neighbors": [
                    {
                        "rank": 40,
                        "user_id": "123e4567-e89b-12d3-a456-426614174002",
                        "handle": "ProPlayer",
                        "score": 19000,
                        "run_id": "123e4567-e89b-12d3-a456-426614174003",
                        "created_at": "2024-01-01T11:30:00Z"
                    }
                ],
                "total_count": 2500
            }
        }
    )
