"""Content repository for dungeons, questions, and daily challenges."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, time as dt_time, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload

from ..domain.models import (
    Dungeon, DungeonTier, Question, DailyChallenge
)
from ..domain.enums import DungeonCategory, QuestionDifficulty


class ContentRepository:
    """Repository for content-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Dungeon operations
    async def get_all_dungeons(self) -> List[Dungeon]:
        """Get all dungeons with their tiers."""
        result = await self.session.execute(
            select(Dungeon)
            .options(selectinload(Dungeon.tiers))
            .order_by(Dungeon.title)
        )
        return list(result.scalars().all())

    async def get_dungeon_by_id(self, dungeon_id: UUID) -> Optional[Dungeon]:
        """Get dungeon by ID with tiers."""
        result = await self.session.execute(
            select(Dungeon)
            .options(selectinload(Dungeon.tiers))
            .where(Dungeon.id == dungeon_id)
        )
        return result.scalar_one_or_none()

    async def get_dungeons_by_category(self, category: DungeonCategory) -> List[Dungeon]:
        """Get dungeons by category."""
        result = await self.session.execute(
            select(Dungeon)
            .options(selectinload(Dungeon.tiers))
            .where(Dungeon.category == category)
            .order_by(Dungeon.title)
        )
        return list(result.scalars().all())

    # Question operations
    async def get_questions_for_dungeon(
        self,
        dungeon_id: UUID,
        difficulty: Optional[QuestionDifficulty] = None,
        limit: Optional[int] = None
    ) -> List[Question]:
        """Get questions for a dungeon, optionally filtered by difficulty."""
        query = select(Question).where(Question.dungeon_id == dungeon_id)
        
        if difficulty:
            query = query.where(Question.difficulty == difficulty)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_questions_by_category_and_difficulty(
        self,
        category: DungeonCategory,
        difficulty: QuestionDifficulty,
        session: AsyncSession = None
    ) -> List[Question]:
        """Get questions by category and difficulty."""
        query = select(Question).where(
            and_(
                Question.dungeon_id.in_(
                    select(Dungeon.id).where(Dungeon.category == category)
                ),
                Question.difficulty == difficulty
            )
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_question_by_hash(self, question_hash: str, session: AsyncSession = None) -> Optional[Question]:
        """Get question by hash to prevent duplicates."""
        # For now, we'll use prompt as a simple hash check
        # In production, you might want to add a hash column to the questions table
        query = select(Question).where(Question.prompt == question_hash)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_daily_challenge_by_date(self, challenge_date) -> Optional[DailyChallenge]:
        """Get daily challenge for a specific date."""
        result = await self.session.execute(
            select(DailyChallenge)
            .options(selectinload(DailyChallenge.dungeon))
            .where(func.date(DailyChallenge.date) == challenge_date)
        )
        return result.scalar_one_or_none()

    async def create_question(
        self,
        dungeon_id: UUID,
        prompt: str,
        choices: List[str],
        answer_index: int,
        difficulty: QuestionDifficulty,
        tags: List[str] = None
    ) -> Question:
        """Create a new question."""
        question = Question(
            dungeon_id=dungeon_id,
            prompt=prompt,
            choices=choices,
            answer_index=answer_index,
            difficulty=difficulty,
            tags=tags or []
        )
        self.session.add(question)
        await self.session.flush()
        await self.session.refresh(question)
        return question

    async def get_question_by_id(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID."""
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_questions_deterministic(
        self,
        dungeon_id: UUID,
        seed: int,
        count: int = 10,
        floor: Optional[int] = None,
        difficulty_weights: Optional[dict] = None
    ) -> List[Question]:
        """Get questions deterministically based on seed."""
        import random
        
        # Create seeded random generator
        rng = random.Random(seed ^ hash(str(dungeon_id)) ^ (floor or 0))
        
        # Get all questions for the dungeon
        all_questions = await self.get_questions_for_dungeon(dungeon_id)
        
        if not all_questions:
            return []
        
        # If we need difficulty balancing and have weights
        if difficulty_weights and len(all_questions) >= count:
            selected_questions = []
            questions_by_difficulty = {
                QuestionDifficulty.EASY: [q for q in all_questions if q.difficulty == QuestionDifficulty.EASY],
                QuestionDifficulty.MEDIUM: [q for q in all_questions if q.difficulty == QuestionDifficulty.MEDIUM],
                QuestionDifficulty.HARD: [q for q in all_questions if q.difficulty == QuestionDifficulty.HARD],
            }
            
            # Select questions based on difficulty weights
            for difficulty, weight in difficulty_weights.items():
                target_count = int(count * weight)
                available = questions_by_difficulty.get(difficulty, [])
                if available:
                    selected = rng.sample(available, min(target_count, len(available)))
                    selected_questions.extend(selected)
            
            # Fill remaining slots if needed
            remaining_count = count - len(selected_questions)
            if remaining_count > 0:
                used_ids = {q.id for q in selected_questions}
                remaining = [q for q in all_questions if q.id not in used_ids]
                if remaining:
                    additional = rng.sample(remaining, min(remaining_count, len(remaining)))
                    selected_questions.extend(additional)
            
            # Shuffle final selection
            rng.shuffle(selected_questions)
            return selected_questions[:count]
        else:
            # Simple random selection
            return rng.sample(all_questions, min(count, len(all_questions)))

    async def count_questions_by_dungeon(self, dungeon_id: UUID) -> int:
        """Count questions for a dungeon."""
        result = await self.session.execute(
            select(func.count(Question.id)).where(Question.dungeon_id == dungeon_id)
        )
        return result.scalar() or 0

    # Daily challenge operations
    async def get_daily_challenge(self, challenge_date: date) -> Optional[DailyChallenge]:
        """Get daily challenge for a specific date."""
        result = await self.session.execute(
            select(DailyChallenge)
            .options(selectinload(DailyChallenge.dungeon))
            .where(func.date(DailyChallenge.date) == challenge_date)
        )
        return result.scalar_one_or_none()

    async def get_current_daily_challenge(self) -> Optional[DailyChallenge]:
        """Get the current active daily challenge."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(DailyChallenge)
            .options(selectinload(DailyChallenge.dungeon))
            .where(
                and_(
                    DailyChallenge.date <= now,
                    DailyChallenge.expires_at > now
                )
            )
            .order_by(DailyChallenge.date.desc())
        )
        return result.scalar_one_or_none()

    async def create_daily_challenge(
        self,
        challenge_date: date,
        seed: int,
        dungeon_id: UUID,
        modifiers: Optional[dict] = None,
        expires_at: Optional[datetime] = None
    ) -> DailyChallenge:
        """Create a new daily challenge."""
        if expires_at is None:
            # Default to expire at the end of the day
            expires_at = datetime.combine(challenge_date, dt_time.max).replace(tzinfo=timezone.utc)

        challenge = DailyChallenge(
            date=datetime.combine(challenge_date, dt_time.min).replace(tzinfo=timezone.utc),
            seed=seed,
            dungeon_id=dungeon_id,
            modifiers=modifiers or {},
            expires_at=expires_at
        )
        self.session.add(challenge)
        await self.session.flush()
        await self.session.refresh(challenge)
        return challenge

    async def get_recent_daily_challenges(self, limit: int = 30) -> List[DailyChallenge]:
        """Get recent daily challenges."""
        result = await self.session.execute(
            select(DailyChallenge)
            .options(selectinload(DailyChallenge.dungeon))
            .order_by(DailyChallenge.date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # Utility methods
    async def get_content_stats(self) -> dict:
        """Get content statistics."""
        # Count dungeons by category
        dungeons_result = await self.session.execute(
            select(Dungeon.category, func.count(Dungeon.id))
            .group_by(Dungeon.category)
        )
        dungeons_by_category = dict(dungeons_result.all())

        # Count questions by difficulty
        questions_result = await self.session.execute(
            select(Question.difficulty, func.count(Question.id))
            .group_by(Question.difficulty)
        )
        questions_by_difficulty = dict(questions_result.all())

        # Total counts
        total_dungeons = await self.session.execute(
            select(func.count(Dungeon.id))
        )
        total_questions = await self.session.execute(
            select(func.count(Question.id))
        )

        return {
            "total_dungeons": total_dungeons.scalar() or 0,
            "total_questions": total_questions.scalar() or 0,
            "dungeons_by_category": dungeons_by_category,
            "questions_by_difficulty": questions_by_difficulty
        }
