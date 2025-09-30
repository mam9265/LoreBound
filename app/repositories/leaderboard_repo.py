"""Leaderboard repository for ranking management."""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from sqlalchemy.orm import selectinload

from ..domain.models import LeaderboardSnapshot, Score, User, Run, Profile
from ..domain.enums import LeaderboardScope


class LeaderboardRepository:
    """Repository for leaderboard-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_top_scores_for_period(
        self,
        scope: LeaderboardScope,
        period_key: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Score]:
        """Get top scores for a specific leaderboard period."""
        # Calculate time filter based on scope and period
        time_filter = self._get_time_filter_for_period(scope, period_key)
        
        query = (
            select(Score)
            .options(
                selectinload(Score.user).selectinload(User.profile),
                selectinload(Score.run)
            )
            .order_by(desc(Score.score))
        )
        
        if time_filter:
            query = query.where(Score.created_at >= time_filter)
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_rank_in_period(
        self,
        user_id: UUID,
        scope: LeaderboardScope,
        period_key: str
    ) -> Optional[int]:
        """Get user's rank in a specific leaderboard period."""
        # Get user's best score for the period
        time_filter = self._get_time_filter_for_period(scope, period_key)
        
        user_score_query = (
            select(func.max(Score.score))
            .where(Score.user_id == user_id)
        )
        
        if time_filter:
            user_score_query = user_score_query.where(Score.created_at >= time_filter)
        
        user_score_result = await self.session.execute(user_score_query)
        user_score = user_score_result.scalar()
        
        if user_score is None:
            return None
        
        # Count how many users have a higher best score
        higher_scores_query = (
            select(func.count(func.distinct(Score.user_id)))
            .where(Score.score > user_score)
        )
        
        if time_filter:
            higher_scores_query = higher_scores_query.where(Score.created_at >= time_filter)
        
        higher_scores_result = await self.session.execute(higher_scores_query)
        higher_scores_count = higher_scores_result.scalar() or 0
        
        return higher_scores_count + 1

    async def get_user_neighbors_in_leaderboard(
        self,
        user_id: UUID,
        scope: LeaderboardScope,
        period_key: str,
        neighbors_count: int = 5
    ) -> Tuple[Optional[Score], List[Score]]:
        """Get user's score and neighboring scores in leaderboard."""
        # Get user's best score for the period
        time_filter = self._get_time_filter_for_period(scope, period_key)
        
        user_score_query = (
            select(Score)
            .options(
                selectinload(Score.user).selectinload(User.profile),
                selectinload(Score.run)
            )
            .where(Score.user_id == user_id)
            .order_by(desc(Score.score))
        )
        
        if time_filter:
            user_score_query = user_score_query.where(Score.created_at >= time_filter)
        
        user_score_result = await self.session.execute(user_score_query)
        user_score = user_score_result.scalar_one_or_none()
        
        if not user_score:
            return None, []
        
        # Get neighbors (scores around user's score)
        neighbors_query = (
            select(Score)
            .options(
                selectinload(Score.user).selectinload(User.profile),
                selectinload(Score.run)
            )
            .where(
                and_(
                    Score.score.between(
                        user_score.score - 1000,  # Adjust range as needed
                        user_score.score + 1000
                    ),
                    Score.user_id != user_id
                )
            )
            .order_by(desc(Score.score))
            .limit(neighbors_count * 2)  # Get more to filter
        )
        
        if time_filter:
            neighbors_query = neighbors_query.where(Score.created_at >= time_filter)
        
        neighbors_result = await self.session.execute(neighbors_query)
        neighbors = list(neighbors_result.scalars().all())
        
        return user_score, neighbors[:neighbors_count]

    async def create_leaderboard_snapshot(
        self,
        scope: LeaderboardScope,
        period_key: str,
        payload: Dict[str, Any]
    ) -> LeaderboardSnapshot:
        """Create a leaderboard snapshot for persistence."""
        snapshot = LeaderboardSnapshot(
            scope=scope,
            period_key=period_key,
            payload=payload,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(snapshot)
        await self.session.flush()
        await self.session.refresh(snapshot)
        return snapshot

    async def get_leaderboard_snapshot(
        self,
        scope: LeaderboardScope,
        period_key: str
    ) -> Optional[LeaderboardSnapshot]:
        """Get a leaderboard snapshot."""
        result = await self.session.execute(
            select(LeaderboardSnapshot)
            .where(
                and_(
                    LeaderboardSnapshot.scope == scope,
                    LeaderboardSnapshot.period_key == period_key
                )
            )
            .order_by(desc(LeaderboardSnapshot.created_at))
        )
        return result.scalar_one_or_none()

    async def get_recent_snapshots(
        self,
        scope: LeaderboardScope,
        limit: int = 10
    ) -> List[LeaderboardSnapshot]:
        """Get recent leaderboard snapshots for a scope."""
        result = await self.session.execute(
            select(LeaderboardSnapshot)
            .where(LeaderboardSnapshot.scope == scope)
            .order_by(desc(LeaderboardSnapshot.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_participants_in_period(
        self,
        scope: LeaderboardScope,
        period_key: str
    ) -> int:
        """Count unique participants in a leaderboard period."""
        time_filter = self._get_time_filter_for_period(scope, period_key)
        
        query = select(func.count(func.distinct(Score.user_id)))
        
        if time_filter:
            query = query.where(Score.created_at >= time_filter)
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_leaderboard_stats(
        self,
        scope: LeaderboardScope,
        period_key: str
    ) -> Dict[str, Any]:
        """Get comprehensive leaderboard statistics."""
        time_filter = self._get_time_filter_for_period(scope, period_key)
        
        # Participant count
        participants = await self.count_participants_in_period(scope, period_key)
        
        # Score statistics
        stats_query = select(
            func.count(Score.id),
            func.avg(Score.score),
            func.max(Score.score),
            func.min(Score.score)
        )
        
        if time_filter:
            stats_query = stats_query.where(Score.created_at >= time_filter)
        
        stats_result = await self.session.execute(stats_query)
        stats_row = stats_result.one()
        
        total_scores = stats_row[0] or 0
        avg_score = float(stats_row[1] or 0)
        max_score = stats_row[2] or 0
        min_score = stats_row[3] or 0
        
        return {
            "scope": scope.value,
            "period_key": period_key,
            "participants": participants,
            "total_scores": total_scores,
            "average_score": avg_score,
            "highest_score": max_score,
            "lowest_score": min_score,
            "last_updated": datetime.now(timezone.utc)
        }

    def _get_time_filter_for_period(
        self,
        scope: LeaderboardScope,
        period_key: str
    ) -> Optional[datetime]:
        """Get time filter for a specific leaderboard period."""
        if scope == LeaderboardScope.ALLTIME:
            return None
        
        try:
            if scope == LeaderboardScope.TODAY:
                # period_key format: "2024-01-01"
                date_obj = datetime.strptime(period_key, "%Y-%m-%d")
                return date_obj.replace(tzinfo=timezone.utc)
            
            elif scope == LeaderboardScope.WEEKLY:
                # period_key format: "2024-W01"
                year, week = period_key.split("-W")
                # Calculate first day of the week
                from datetime import timedelta
                jan_1 = datetime(int(year), 1, 1, tzinfo=timezone.utc)
                # Find the first Monday of the year
                days_to_monday = (7 - jan_1.weekday()) % 7
                first_monday = jan_1 + timedelta(days=days_to_monday)
                # Calculate the start of the specified week
                week_start = first_monday + timedelta(weeks=int(week) - 1)
                return week_start
        
        except (ValueError, AttributeError):
            # If period_key is malformed, return None (no filter)
            pass
        
        return None

    async def get_user_best_scores_summary(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's best scores across different dungeons."""
        # Get user's best score per dungeon
        subquery = (
            select(
                Run.dungeon_id,
                func.max(Score.score).label("best_score")
            )
            .join(Score, Score.run_id == Run.id)
            .where(Score.user_id == user_id)
            .group_by(Run.dungeon_id)
            .subquery()
        )
        
        # Get the actual score records for those best scores
        query = (
            select(Score)
            .options(
                selectinload(Score.run).selectinload(Run.dungeon)
            )
            .join(Run, Score.run_id == Run.id)
            .join(
                subquery,
                and_(
                    Run.dungeon_id == subquery.c.dungeon_id,
                    Score.score == subquery.c.best_score
                )
            )
            .where(Score.user_id == user_id)
            .order_by(desc(Score.score))
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        scores = result.scalars().all()
        
        summary = []
        for score in scores:
            summary.append({
                "dungeon_id": score.run.dungeon_id,
                "dungeon_title": score.run.dungeon.title,
                "best_score": score.score,
                "floor_reached": score.floor,
                "correct_answers": score.correct_count,
                "achieved_at": score.created_at
            })
        
        return summary
