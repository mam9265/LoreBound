"""Game run schemas for starting and submitting runs."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import RunStatus


class StartRunRequest(BaseModel):
    """Start run request schema."""
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    is_daily: bool = Field(default=False, description="Whether this is a daily challenge run")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_daily": False
            }
        }
    )


class StartRunResponse(BaseModel):
    """Start run response schema."""
    run_id: UUID = Field(..., description="Run unique identifier")
    seed: int = Field(..., description="Deterministic seed for the run")
    session_token: str = Field(..., description="Session token for anti-cheat verification")
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    started_at: datetime = Field(..., description="Run start timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "seed": 12345,
                "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174001",
                "started_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class TurnData(BaseModel):
    """Individual turn data for run submission."""
    i: int = Field(..., description="Turn index", alias="turn_index")
    qid: str = Field(..., description="Question ID", alias="question_id")
    a: int = Field(..., description="Selected answer index", alias="answer_index")
    c: bool = Field(..., description="Whether answer was correct", alias="correct")
    t: int = Field(..., description="Time taken in milliseconds", alias="time_ms")
    ts: int = Field(..., description="Client timestamp", alias="timestamp")
    h: str = Field(..., description="HMAC signature for this turn", alias="hmac")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "i": 0,
                "qid": "123e4567-e89b-12d3-a456-426614174000",
                "a": 2,
                "c": True,
                "t": 1820,
                "ts": 1699999990000,
                "h": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class SubmitRunRequest(BaseModel):
    """Submit run request schema."""
    run_id: UUID = Field(..., description="Run identifier")
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: int = Field(..., ge=1, description="Floor reached")
    total_time_ms: int = Field(..., ge=0, description="Total time taken in milliseconds")
    correct_count: int = Field(..., ge=0, description="Number of correct answers")
    streak_max: int = Field(..., ge=0, description="Maximum streak achieved")
    seed: int = Field(..., description="Run seed (must match start run)")
    turns: List[TurnData] = Field(..., description="Turn-by-turn data")
    client_signature: str = Field(..., description="Client-computed aggregate signature")
    is_victory: bool = Field(default=True, description="Whether the player won/cleared the dungeon")
    is_daily_challenge: bool = Field(default=False, description="Whether this was a daily challenge")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174001",
                "floor": 3,
                "total_time_ms": 74210,
                "correct_count": 24,
                "streak_max": 7,
                "seed": 12345,
                "turns": [
                    {
                        "i": 0,
                        "qid": "123e4567-e89b-12d3-a456-426614174002",
                        "a": 2,
                        "c": True,
                        "t": 1820,
                        "ts": 1699999990000,
                        "h": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                ],
                "client_signature": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class ScoreResponse(BaseModel):
    """Score response schema."""
    id: UUID = Field(..., description="Score unique identifier")
    run_id: UUID = Field(..., description="Run identifier")
    user_id: UUID = Field(..., description="User identifier")
    floor: int = Field(..., description="Floor reached")
    correct_count: int = Field(..., description="Correct answers")
    total_time_ms: int = Field(..., description="Total time taken")
    streak_max: int = Field(..., description="Maximum streak")
    score: int = Field(..., description="Final calculated score")
    created_at: datetime = Field(..., description="Score creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "run_id": "123e4567-e89b-12d3-a456-426614174001",
                "user_id": "123e4567-e89b-12d3-a456-426614174002",
                "floor": 3,
                "correct_count": 24,
                "total_time_ms": 74210,
                "streak_max": 7,
                "score": 18500,
                "created_at": "2024-01-01T12:15:30Z"
            }
        }
    )


class SubmitRunResponse(BaseModel):
    """Submit run response schema."""
    score: ScoreResponse = Field(..., description="Score details")
    rank: Optional[int] = Field(None, description="Current leaderboard rank")
    verification_status: str = Field(..., description="Anti-cheat verification status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "run_id": "123e4567-e89b-12d3-a456-426614174001",
                    "user_id": "123e4567-e89b-12d3-a456-426614174002",
                    "floor": 3,
                    "correct_count": 24,
                    "total_time_ms": 74210,
                    "streak_max": 7,
                    "score": 18500,
                    "created_at": "2024-01-01T12:15:30Z"
                },
                "rank": 42,
                "verification_status": "verified"
            }
        }
    )


# Add missing schemas that our service expects
class RunStartRequest(BaseModel):
    """Run start request schema (alias for StartRunRequest)."""
    dungeon_id: UUID = Field(..., description="Dungeon identifier")
    floor: int = Field(default=1, ge=1, le=100, description="Starting floor")
    client_metadata: Dict[str, Any] = Field(default_factory=dict, description="Client metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dungeon_id": "123e4567-e89b-12d3-a456-426614174000",
                "floor": 1,
                "client_metadata": {"device": "iOS", "version": "1.0.0"}
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "points": 100,
                "answer_time": 1.82,
                "is_correct": True,
                "streak_bonus": 10,
                "time_bonus": 5
            }
        }
    )


class RunSubmitRequest(BaseModel):
    """Run submit request schema."""
    turn_data: List[TurnData] = Field(..., description="Turn-by-turn data")
    scores: List[ScoreData] = Field(..., description="Score data for each turn")
    client_signature: str = Field(..., description="Client-computed aggregate signature")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "turn_data": [
                    {
                        "i": 0,
                        "qid": "123e4567-e89b-12d3-a456-426614174000",
                        "a": 2,
                        "c": True,
                        "t": 1820,
                        "ts": 1699999990000,
                        "h": "signature..."
                    }
                ],
                "scores": [
                    {
                        "points": 100,
                        "answer_time": 1.82,
                        "is_correct": True,
                        "streak_bonus": 10,
                        "time_bonus": 5
                    }
                ],
                "client_signature": "aggregate_signature..."
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
                "completed_at": "2024-01-01T12:15:30Z"
            }
        }
    )


class RunStatsResponse(BaseModel):
    """Run statistics response schema."""
    total_runs: int = Field(..., description="Total runs completed")
    total_score: int = Field(..., description="Total score across all runs")
    average_score: float = Field(..., description="Average score per run")
    best_score: int = Field(..., description="Best single run score")
    total_correct: int = Field(..., description="Total correct answers")
    total_questions: int = Field(..., description="Total questions answered")
    accuracy_percentage: float = Field(..., description="Overall accuracy percentage")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_runs": 25,
                "total_score": 42500,
                "average_score": 1700.0,
                "best_score": 2350,
                "total_correct": 485,
                "total_questions": 600,
                "accuracy_percentage": 80.83
            }
        }
    )
