"""Content schemas for dungeons, questions, and daily challenges."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import DungeonCategory, QuestionDifficulty


class DungeonMetaResponse(BaseModel):
    """Dungeon metadata response schema."""
    id: UUID = Field(..., description="Dungeon unique identifier")
    title: str = Field(..., description="Dungeon title")
    category: DungeonCategory = Field(..., description="Dungeon category")
    content_version: int = Field(..., description="Content version")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Sports Legends",
                "category": "sports",
                "content_version": 1
            }
        }
    )


class DungeonTierResponse(BaseModel):
    """Dungeon tier/floor response schema."""
    id: UUID = Field(..., description="Tier unique identifier")
    floor: int = Field(..., description="Floor number")
    boss_meta: Dict[str, Any] = Field(default_factory=dict, description="Boss metadata")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "floor": 5,
                "boss_meta": {
                    "name": "Sports Trivia Master",
                    "difficulty": "hard",
                    "questions_count": 10
                }
            }
        }
    )


class DungeonResponse(BaseModel):
    """Complete dungeon response schema."""
    id: UUID = Field(..., description="Dungeon unique identifier")
    title: str = Field(..., description="Dungeon title")
    category: DungeonCategory = Field(..., description="Dungeon category")
    modifiers: Dict[str, Any] = Field(default_factory=dict, description="Dungeon modifiers")
    content_version: int = Field(..., description="Content version")
    tiers: List[DungeonTierResponse] = Field(default_factory=list, description="Dungeon tiers/floors")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Sports Legends",
                "category": "sports",
                "modifiers": {
                    "time_limit": 30,
                    "streak_bonus": 1.5
                },
                "content_version": 1,
                "tiers": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "floor": 1,
                        "boss_meta": {"name": "Rookie Champion", "difficulty": "easy"}
                    }
                ]
            }
        }
    )


class QuestionResponse(BaseModel):
    """Question response schema."""
    id: UUID = Field(..., description="Question unique identifier")
    prompt: str = Field(..., description="Question text")
    choices: List[str] = Field(..., description="Answer choices")
    difficulty: QuestionDifficulty = Field(..., description="Question difficulty")
    tags: List[str] = Field(default_factory=list, description="Question tags")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "prompt": "Which team won the NBA championship in 2023?",
                "choices": [
                    "Denver Nuggets",
                    "Miami Heat", 
                    "Boston Celtics",
                    "Golden State Warriors"
                ],
                "difficulty": "medium",
                "tags": ["NBA", "2023", "championship"]
            }
        }
    )


class QuestionsRequest(BaseModel):
    """Questions request query parameters."""
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: Optional[int] = Field(None, ge=1, le=100, description="Floor number")
    seed: Optional[int] = Field(None, description="Deterministic seed for question selection")
    count: int = Field(default=10, ge=1, le=50, description="Number of questions to return")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174000",
                "floor": 3,
                "seed": 12345,
                "count": 15
            }
        }
    )


class QuestionsResponse(BaseModel):
    """Questions response schema."""
    questions: List[QuestionResponse] = Field(..., description="List of questions")
    seed: int = Field(..., description="Seed used for question selection")
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: Optional[int] = Field(None, description="Floor number")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "questions": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "prompt": "Which team won the NBA championship in 2023?",
                        "choices": ["Denver Nuggets", "Miami Heat", "Boston Celtics", "Golden State Warriors"],
                        "difficulty": "medium",
                        "tags": ["NBA", "2023", "championship"]
                    }
                ],
                "seed": 12345,
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174000",
                "floor": 3
            }
        }
    )


class DailyChallengeResponse(BaseModel):
    """Daily challenge response schema."""
    id: UUID = Field(..., description="Daily challenge identifier")
    date: datetime = Field(..., description="Challenge date")
    seed: int = Field(..., description="Challenge seed")
    dungeon: DungeonMetaResponse = Field(..., description="Challenge dungeon")
    modifiers: Dict[str, Any] = Field(default_factory=dict, description="Challenge modifiers")
    expires_at: datetime = Field(..., description="Challenge expiration time")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2024-01-01T00:00:00Z",
                "seed": 20240101,
                "dungeon": {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "title": "Music Maestros",
                    "category": "music",
                    "content_version": 1
                },
                "modifiers": {
                    "double_xp": True,
                    "time_bonus": 1.2
                },
                "expires_at": "2024-01-02T00:00:00Z"
            }
        }
    )


class QuestionRequest(BaseModel):
    """Request schema for creating questions."""
    question_text: str = Field(..., min_length=10, max_length=500, description="Question text")
    choices: List[str] = Field(..., min_items=2, max_items=6, description="Answer choices")
    correct_choice_index: int = Field(..., ge=0, description="Index of correct answer in choices")
    category: DungeonCategory = Field(..., description="Question category")
    difficulty: QuestionDifficulty = Field(..., description="Question difficulty")
    source: str = Field(default="manual", description="Question source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question_text": "Which planet is closest to the Sun?",
                "choices": ["Mercury", "Venus", "Earth", "Mars"],
                "correct_choice_index": 0,
                "category": "science",
                "difficulty": "easy",
                "source": "external_api",
                "metadata": {
                    "source_id": "opentdb_12345",
                    "api_provider": "opentdb"
                }
            }
        }
    )