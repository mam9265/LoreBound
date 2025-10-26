"""Domain models and database entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, DateTime, Integer, String, Text, JSON, ARRAY,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .enums import (
    DungeonCategory, ItemSlot, ItemRarity, 
    QuestionDifficulty, LeaderboardScope, UserStatus
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    apple_sub: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    status: Mapped[UserStatus] = mapped_column(String(20), default=UserStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False)
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="user")
    achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user")
    runs: Mapped[list["Run"]] = relationship("Run", back_populates="user")
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="user")


class Profile(Base):
    """User profile model."""
    __tablename__ = "profiles"
    
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    handle: Mapped[str] = mapped_column(String(50), unique=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    avatar_layers: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")


class Item(Base):
    """Game item model."""
    __tablename__ = "items"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    slot: Mapped[ItemSlot] = mapped_column(String(20))
    rarity: Mapped[ItemRarity] = mapped_column(String(20))
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="item")


class Inventory(Base):
    """User inventory model."""
    __tablename__ = "inventory"
    
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    item_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("items.id"), primary_key=True)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="inventory")
    item: Mapped["Item"] = relationship("Item", back_populates="inventory")
    
    __table_args__ = (
        Index("idx_inventory_user_equipped", user_id, equipped),
    )


class Achievement(Base):
    """Achievement definition model."""
    __tablename__ = "achievements"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    criteria: Mapped[dict] = mapped_column(JSON)
    
    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """User achievement progress model."""
    __tablename__ = "user_achievements"
    
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    achievement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("achievements.id"), primary_key=True)
    progress: Mapped[dict] = mapped_column(JSON, default=dict)
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")


class Dungeon(Base):
    """Dungeon model."""
    __tablename__ = "dungeons"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(100))
    category: Mapped[DungeonCategory] = mapped_column(String(20))
    modifiers: Mapped[dict] = mapped_column(JSON, default=dict)
    content_version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    tiers: Mapped[list["DungeonTier"]] = relationship("DungeonTier", back_populates="dungeon")
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="dungeon")
    daily_challenges: Mapped[list["DailyChallenge"]] = relationship("DailyChallenge", back_populates="dungeon")
    runs: Mapped[list["Run"]] = relationship("Run", back_populates="dungeon")


class DungeonTier(Base):
    """Dungeon tier/floor model."""
    __tablename__ = "dungeon_tiers"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    dungeon_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("dungeons.id"))
    floor: Mapped[int] = mapped_column(Integer)
    boss_meta: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    dungeon: Mapped["Dungeon"] = relationship("Dungeon", back_populates="tiers")
    
    __table_args__ = (
        UniqueConstraint("dungeon_id", "floor", name="uq_dungeon_tier"),
        Index("idx_dungeon_tiers_dungeon_floor", dungeon_id, floor),
    )


class Question(Base):
    """Question model."""
    __tablename__ = "questions"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    dungeon_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("dungeons.id"))
    prompt: Mapped[str] = mapped_column(Text)
    choices: Mapped[list] = mapped_column(JSON)  # Array of choice strings
    answer_index: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(String(20))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Relationships
    dungeon: Mapped["Dungeon"] = relationship("Dungeon", back_populates="questions")
    
    __table_args__ = (
        Index("idx_questions_dungeon_difficulty", dungeon_id, difficulty),
    )


class DailyChallenge(Base):
    """Daily challenge model."""
    __tablename__ = "daily_challenges"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), unique=True)
    seed: Mapped[int] = mapped_column(Integer)
    dungeon_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("dungeons.id"))
    modifiers: Mapped[dict] = mapped_column(JSON, default=dict)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    dungeon: Mapped["Dungeon"] = relationship("Dungeon", back_populates="daily_challenges")


class Run(Base):
    """Game run model."""
    __tablename__ = "runs"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    dungeon_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("dungeons.id"))
    seed: Mapped[int] = mapped_column(Integer)
    floor: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    session_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="runs")
    dungeon: Mapped["Dungeon"] = relationship("Dungeon", back_populates="runs")
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="run")
    
    __table_args__ = (
        Index("idx_runs_user_created", user_id, started_at),
        Index("idx_runs_status", status),
    )


class Score(Base):
    """Score model."""
    __tablename__ = "scores"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("runs.id"))
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    floor: Mapped[int] = mapped_column(Integer)
    correct_count: Mapped[int] = mapped_column(Integer)
    total_time_ms: Mapped[int] = mapped_column(Integer)
    streak_max: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="scores")
    user: Mapped["User"] = relationship("User", back_populates="scores")
    
    __table_args__ = (
        Index("idx_scores_user_created", user_id, created_at),
        Index("idx_scores_score", score.desc()),
    )


class LeaderboardSnapshot(Base):
    """Leaderboard snapshot model."""
    __tablename__ = "leaderboard_snapshots"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    scope: Mapped[LeaderboardScope] = mapped_column(String(20))
    period_key: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_leaderboard_snapshots_scope_period", scope, period_key),
    )


class FeatureFlag(Base):
    """Feature flag model."""
    __tablename__ = "feature_flags"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
