"""Domain enums and constants."""

from enum import Enum


class DungeonCategory(str, Enum):
    """Dungeon category types."""
    SPORTS = "sports"
    MUSIC = "music"
    HISTORY = "history"
    POP_CULTURE = "pop_culture"


class ItemSlot(str, Enum):
    """Equipment slot types."""
    HELMET = "helmet"
    ARMOR = "armor"
    WEAPON = "weapon"
    SHIELD = "shield"
    BOOTS = "boots"
    RING = "ring"
    AMULET = "amulet"


class ItemRarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class QuestionDifficulty(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LeaderboardScope(str, Enum):
    """Leaderboard time scopes."""
    TODAY = "today"
    WEEKLY = "weekly"
    ALLTIME = "alltime"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class RunStatus(str, Enum):
    """Game run status."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"