"""Run and score repository for game session management."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from ..domain.models import Run, Score


class RunRepository:
    """Repository for run and score-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(
        self,
        user_id: UUID,
        dungeon_id: UUID,
        seed: int,
        floor: int = 1,
        session_token: Optional[str] = None,
        summary: Optional[Dict[str, Any]] = None
    ) -> Run:
        """Create a new game run."""
        run = Run(
            user_id=user_id,
            dungeon_id=dungeon_id,
            seed=seed,
            floor=floor,
            session_token=session_token,
            status="in_progress",
            summary=summary or {},
            started_at=datetime.now(timezone.utc)
        )
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: UUID) -> Optional[Run]:
        """Get run by ID."""
        result = await self.session.execute(
            select(Run)
            .options(
                selectinload(Run.user),
                selectinload(Run.dungeon),
                selectinload(Run.scores)
            )
            .where(Run.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_user_runs(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        completed_only: bool = False
    ) -> List[Run]:
        """Get runs for a specific user."""
        query = (
            select(Run)
            .options(selectinload(Run.dungeon), selectinload(Run.scores))
            .where(Run.user_id == user_id)
        )
        
        if completed_only:
            query = query.where(Run.completed_at.is_not(None))
        
        query = query.order_by(desc(Run.started_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def complete_run(
        self,
        run_id: UUID,
        total_score: int,
        summary: Dict[str, Any],
        signature: str
    ) -> Run:
        """Mark a run as completed with summary and signature."""
        from sqlalchemy import update
        
        result = await self.session.execute(
            update(Run)
            .where(Run.id == run_id)
            .values(
                status="completed",
                completed_at=datetime.now(timezone.utc),
                total_score=total_score,
                summary=summary,
                signature=signature
            )
            .returning(Run)
        )
        return result.scalar_one()
    
    async def abandon_run(
        self,
        run_id: UUID
    ) -> Run:
        """Mark a run as abandoned."""
        from sqlalchemy import update
        
        result = await self.session.execute(
            update(Run)
            .where(Run.id == run_id)
            .values(
                status="abandoned",
                completed_at=datetime.now(timezone.utc)
            )
            .returning(Run)
        )
        return result.scalar_one()
    
    async def get_by_id(self, run_id: UUID) -> Optional[Run]:
        """Get run by ID (alias for get_run_by_id)."""
        return await self.get_run_by_id(run_id)
    
    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's run statistics."""
        # Get total runs
        total_runs_query = select(func.count(Run.id)).where(
            and_(Run.user_id == user_id, Run.status == "completed")
        )
        total_runs = (await self.session.execute(total_runs_query)).scalar() or 0
        
        # Get score statistics
        score_stats_query = select(
            func.sum(Score.score),
            func.avg(Score.score),
            func.max(Score.score),
            func.sum(Score.correct_count),
            func.sum(Score.correct_count) + func.count(Score.id) - func.sum(Score.correct_count)
        ).where(Score.user_id == user_id)
        
        stats_result = await self.session.execute(score_stats_query)
        stats = stats_result.one()
        
        total_score = stats[0] or 0
        avg_score = float(stats[1] or 0)
        best_score = stats[2] or 0
        total_correct = stats[3] or 0
        total_questions = total_correct + (stats[4] or 0)
        
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "total_runs": total_runs,
            "total_score": total_score,
            "average_score": avg_score,
            "best_score": best_score,
            "total_correct": total_correct,
            "total_questions": total_questions,
            "accuracy_percentage": accuracy
        }

    async def create_score(
        self,
        run_id: UUID,
        user_id: UUID,
        floor: int,
        correct_count: int,
        total_time_ms: int,
        streak_max: int,
        score: int
    ) -> Score:
        """Create a score record."""
        score_record = Score(
            run_id=run_id,
            user_id=user_id,
            floor=floor,
            correct_count=correct_count,
            total_time_ms=total_time_ms,
            streak_max=streak_max,
            score=score,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(score_record)
        await self.session.flush()
        await self.session.refresh(score_record)
        return score_record

    async def get_score_by_id(self, score_id: UUID) -> Optional[Score]:
        """Get score by ID."""
        result = await self.session.execute(
            select(Score)
            .options(
                selectinload(Score.run),
                selectinload(Score.user)
            )
            .where(Score.id == score_id)
        )
        return result.scalar_one_or_none()

    async def get_user_scores(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Score]:
        """Get scores for a specific user."""
        result = await self.session.execute(
            select(Score)
            .options(selectinload(Score.run))
            .where(Score.user_id == user_id)
            .order_by(desc(Score.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_best_score(self, user_id: UUID, dungeon_id: Optional[UUID] = None) -> Optional[Score]:
        """Get user's best score, optionally for a specific dungeon."""
        query = (
            select(Score)
            .options(selectinload(Score.run))
            .where(Score.user_id == user_id)
        )
        
        if dungeon_id:
            query = query.join(Run).where(Run.dungeon_id == dungeon_id)
        
        query = query.order_by(desc(Score.score))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_top_scores(
        self,
        limit: int = 100,
        dungeon_id: Optional[UUID] = None,
        time_filter: Optional[datetime] = None
    ) -> List[Score]:
        """Get top scores with optional filters."""
        query = (
            select(Score)
            .options(
                selectinload(Score.user).selectinload("profile"),
                selectinload(Score.run)
            )
        )
        
        if dungeon_id:
            query = query.join(Run).where(Run.dungeon_id == dungeon_id)
        
        if time_filter:
            query = query.where(Score.created_at >= time_filter)
        
        query = query.order_by(desc(Score.score)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_rank(
        self,
        user_id: UUID,
        score: int,
        dungeon_id: Optional[UUID] = None,
        time_filter: Optional[datetime] = None
    ) -> int:
        """Get user's rank based on their score."""
        query = select(func.count(Score.id)).where(Score.score > score)
        
        if dungeon_id:
            query = query.join(Run).where(Run.dungeon_id == dungeon_id)
        
        if time_filter:
            query = query.where(Score.created_at >= time_filter)
        
        result = await self.session.execute(query)
        higher_scores = result.scalar() or 0
        return higher_scores + 1

    async def get_daily_runs(
        self,
        user_id: UUID,
        date: datetime,
        dungeon_id: Optional[UUID] = None
    ) -> List[Run]:
        """Get user's runs for a specific day."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query = (
            select(Run)
            .options(selectinload(Run.scores))
            .where(
                and_(
                    Run.user_id == user_id,
                    Run.started_at >= start_of_day,
                    Run.started_at <= end_of_day
                )
            )
        )
        
        if dungeon_id:
            query = query.where(Run.dungeon_id == dungeon_id)
        
        query = query.order_by(desc(Run.started_at))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_user_runs(
        self,
        user_id: UUID,
        completed_only: bool = False,
        dungeon_id: Optional[UUID] = None
    ) -> int:
        """Count user's runs with optional filters."""
        query = select(func.count(Run.id)).where(Run.user_id == user_id)
        
        if completed_only:
            query = query.where(Run.completed_at.is_not(None))
        
        if dungeon_id:
            query = query.where(Run.dungeon_id == dungeon_id)
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_run_statistics(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get run statistics, optionally for a specific user."""
        filters = []
        if user_id:
            filters.append(Run.user_id == user_id)
        
        # Total runs
        total_query = select(func.count(Run.id))
        if filters:
            total_query = total_query.where(and_(*filters))
        total_runs = (await self.session.execute(total_query)).scalar() or 0
        
        # Completed runs
        completed_query = select(func.count(Run.id)).where(Run.completed_at.is_not(None))
        if filters:
            completed_query = completed_query.where(and_(*filters))
        completed_runs = (await self.session.execute(completed_query)).scalar() or 0
        
        # Average score
        avg_score_query = select(func.avg(Score.score))
        if user_id:
            avg_score_query = avg_score_query.where(Score.user_id == user_id)
        avg_score = (await self.session.execute(avg_score_query)).scalar() or 0
        
        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "completion_rate": completed_runs / total_runs if total_runs > 0 else 0,
            "average_score": float(avg_score)
        }
