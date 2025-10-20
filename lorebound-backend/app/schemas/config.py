"""Configuration and feature flags schemas."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class FeatureFlagResponse(BaseModel):
    """Feature flag response schema."""
    key: str = Field(..., description="Feature flag key")
    value: Dict[str, Any] = Field(..., description="Feature flag value")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "key": "daily_challenge_enabled",
                "value": {
                    "enabled": True,
                    "reset_hour": 0,
                    "bonus_multiplier": 1.5
                }
            }
        }
    )


class GameConfigResponse(BaseModel):
    """Complete game configuration response schema."""
    feature_flags: List[FeatureFlagResponse] = Field(..., description="Active feature flags")
    game_settings: Dict[str, Any] = Field(..., description="Game configuration settings")
    content_version: int = Field(..., description="Current content version")
    api_version: str = Field(..., description="API version")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "feature_flags": [
                    {
                        "key": "daily_challenge_enabled",
                        "value": {
                            "enabled": True,
                            "reset_hour": 0,
                            "bonus_multiplier": 1.5
                        }
                    },
                    {
                        "key": "leaderboard_enabled",
                        "value": {
                            "enabled": True,
                            "update_interval": 60
                        }
                    }
                ],
                "game_settings": {
                    "streak_cap": 10,
                    "timer_seconds": 30,
                    "base_score_multiplier": 100,
                    "time_bonus_threshold": 5,
                    "difficulty_multipliers": {
                        "easy": 1.0,
                        "medium": 1.5,
                        "hard": 2.0
                    },
                    "reward_rates": {
                        "xp_per_correct": 50,
                        "xp_streak_bonus": 25,
                        "item_drop_chance": 0.1
                    }
                },
                "content_version": 1,
                "api_version": "0.1.0"
            }
        }
    )


class AchievementResponse(BaseModel):
    """Achievement response schema."""
    id: str = Field(..., description="Achievement unique identifier")
    slug: str = Field(..., description="Achievement slug")
    name: str = Field(..., description="Achievement name")
    description: str = Field(..., description="Achievement description")
    criteria: Dict[str, Any] = Field(..., description="Achievement criteria")
    progress: Dict[str, Any] = Field(default_factory=dict, description="User progress on this achievement")
    unlocked: bool = Field(default=False, description="Whether user has unlocked this achievement")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "slug": "first_victory",
                "name": "First Victory",
                "description": "Complete your first dungeon run",
                "criteria": {
                    "type": "runs_completed",
                    "count": 1
                },
                "progress": {
                    "runs_completed": 1
                },
                "unlocked": True
            }
        }
    )
