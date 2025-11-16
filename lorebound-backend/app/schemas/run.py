"""Game run schemas for starting and submitting runs."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import RunStatus
from .content import DungeonMetaResponse


class RunStartRequest(BaseModel):
    """Start run request schema."""
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    is_daily: bool = Field(default=False, description="Whether this is a daily challenge run")
    floor: int = Field(default=1, ge=1, le=100, description="Starting floor number")
    client_metadata: Dict[str, Any] = Field(default_factory=dict, description="Client metadata for anti-cheat")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_daily": False,
                "floor": 1,
                "client_metadata": {"device": "iOS", "version": "1.0.0"}
            }
        }
    )


class ItemBonusResponse(BaseModel):
    """Item bonus information."""
    item_id: UUID = Field(..., description="Item identifier")
    name: str = Field(..., description="Item name")
    slot: str = Field(..., description="Equipment slot")
    rarity: str = Field(..., description="Item rarity")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Item stats providing bonuses")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Sword of Swift Answers",
                "slot": "weapon",
                "rarity": "epic",
                "stats": {
                    "score_multiplier": 1.15,
                    "time_extension": 3
                }
            }
        }
    )


class StartRunResponse(BaseModel):
    """Start run response schema."""
    run_id: UUID = Field(..., description="Run unique identifier")
    seed: int = Field(..., description="Deterministic seed for the run")
    session_token: str = Field(..., description="Anti-cheat session token")
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: int = Field(..., description="Starting floor")
    equipped_items: List[ItemBonusResponse] = Field(default_factory=list, description="Equipped items and their bonuses")
    total_bonuses: Dict[str, float] = Field(default_factory=dict, description="Total combined bonuses from all items")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "seed": 123456,
                "session_token": "session_token_here",
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174002",
                "floor": 1,
                "equipped_items": [
                    {
                        "item_id": "item-1",
                        "name": "Sword of Swift Answers",
                        "slot": "weapon",
                        "rarity": "epic",
                        "stats": {"score_multiplier": 1.15, "time_extension": 3}
                    }
                ],
                "total_bonuses": {
                    "score_multiplier": 1.25,
                    "time_extension": 5,
                    "xp_bonus": 0.1
                }
            }
        }
    )


class AnswerCheckRequest(BaseModel):
    """Answer validation request schema."""
    answer_index: int = Field(..., ge=0, le=3, description="Selected answer index")
    time_taken: float = Field(..., ge=0, description="Time taken to answer in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer_index": 2,
                "time_taken": 1.82
            }
        }
    )


class AnswerCheckResponse(BaseModel):
    """Answer validation response schema."""
    is_correct: bool = Field(..., description="Whether the answer was correct")
    correct_index: int = Field(..., description="The correct answer index")
    explanation: Optional[str] = Field(None, description="Optional explanation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_correct": True,
                "correct_index": 2,
                "explanation": "Great job!"
            }
        }
    )


class TurnData(BaseModel):
    """Turn data for run submission."""
    question_index: int = Field(..., ge=0, description="Question index in the run")
    answer_index: int = Field(..., ge=-1, le=3, description="Selected answer index (-1 for timeout/no answer)")
    time_taken: float = Field(..., ge=0, description="Time taken to answer")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question_index": 0,
                "answer_index": 2,
                "time_taken": 1.82
            }
        }
    )


class ScoreData(BaseModel):
    """Individual score data for run submission."""
    points: int = Field(..., ge=0, description="Points earned")
    answer_time: float = Field(..., ge=0, description="Time taken to answer in seconds")
    is_correct: bool = Field(..., description="Whether answer was correct")
    streak_bonus: int = Field(default=0, ge=0, description="Streak bonus points")
    time_bonus: int = Field(default=0, ge=0, description="Time bonus points")
    item_bonus: int = Field(default=0, ge=0, description="Bonus points from equipped items")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "points": 100,
                "answer_time": 1.82,
                "is_correct": True,
                "streak_bonus": 10,
                "time_bonus": 5,
                "item_bonus": 15
            }
        }
    )


class RunSubmitRequest(BaseModel):
    """Run submit request schema."""
    turn_data: List[TurnData] = Field(..., description="Turn-by-turn data")
    scores: List[ScoreData] = Field(..., description="Score data for each turn")
    client_signature: str = Field(..., description="Client anti-cheat signature")
    is_daily_challenge: bool = Field(default=False, description="Whether this is a daily challenge")
    is_victory: bool = Field(default=True, description="Whether the run was completed successfully")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "turn_data": [
                    {"question_index": 0, "answer_index": 2, "time_taken": 1.82},
                    {"question_index": 1, "answer_index": 1, "time_taken": 2.15}
                ],
                "scores": [
                    {
                        "points": 100,
                        "answer_time": 1.82,
                        "is_correct": True,
                        "streak_bonus": 10,
                        "time_bonus": 5,
                        "item_bonus": 15
                    },
                    {
                        "points": 95,
                        "answer_time": 2.15,
                        "is_correct": True,
                        "streak_bonus": 20,
                        "time_bonus": 3,
                        "item_bonus": 14
                    }
                ],
                "client_signature": "signature_hash_here",
                "is_daily_challenge": False,
                "is_victory": True
            }
        }
    )


class RunResponse(BaseModel):
    """Run response schema."""
    id: UUID = Field(..., description="Run unique identifier")
    user_id: UUID = Field(..., description="User identifier")
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: int = Field(..., description="Floor reached")
    status: RunStatus = Field(..., description="Run status")
    session_token: str = Field(..., description="Session token")
    total_score: Optional[int] = Field(None, description="Total score")
    started_at: datetime = Field(..., description="Run start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Run completion timestamp")
    dungeon: Optional[DungeonMetaResponse] = Field(None, description="Dungeon information")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174002",
                "floor": 3,
                "status": "completed",
                "session_token": "session_token...",
                "total_score": 1850,
                "started_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:15:30Z",
                "dungeon": {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "title": "Sports Arena",
                    "category": "sports",
                    "content_version": 1
                }
            }
        }
    )


class RunStatsResponse(BaseModel):
    """Run statistics response schema."""
    total_runs: int = Field(..., description="Total runs completed")
    total_score: int = Field(..., description="Total accumulated score")
    average_score: float = Field(..., description="Average score per run")
    best_score: int = Field(..., description="Best single run score")
    total_correct: int = Field(..., description="Total correct answers")
    total_questions: int = Field(..., description="Total questions answered")
    accuracy_percentage: float = Field(..., description="Overall accuracy percentage")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_runs": 42,
                "total_score": 50000,
                "average_score": 1190.5,
                "best_score": 2500,
                "total_correct": 380,
                "total_questions": 420,
                "accuracy_percentage": 90.48
            }
        }
    )
