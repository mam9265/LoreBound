"""Leaderboard service for managing rankings and caching."""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.enums import LeaderboardScope
from ..domain.models import Score, User
from ..repositories.leaderboard_repo import LeaderboardRepository
from ..core.redis_client import RedisClient

logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service for leaderboard management with Redis caching."""
    
    # Cache TTLs (in seconds)
    CACHE_TTL_TODAY = 30  # 30 seconds for today's leaderboard
    CACHE_TTL_WEEKLY = 60  # 1 minute for weekly
    CACHE_TTL_ALLTIME = 60  # 1 minute for all-time (reduced for faster updates during testing)
    
    # Cache key prefixes
    KEY_PREFIX_LEADERBOARD = "leaderboard"
    KEY_PREFIX_USER_RANK = "user_rank"
    KEY_PREFIX_STATS = "leaderboard_stats"
    
    def __init__(self, session: AsyncSession, redis: RedisClient):
        self.session = session
        self.redis = redis
        self.repo = LeaderboardRepository(session)
    
    async def invalidate_all_caches(self):
        """Invalidate all leaderboard caches."""
        try:
            # Delete all leaderboard cache keys
            pattern = f"{self.KEY_PREFIX_LEADERBOARD}:*"
            await self.redis.delete_pattern(pattern)
            
            pattern = f"{self.KEY_PREFIX_USER_RANK}:*"
            await self.redis.delete_pattern(pattern)
            
            pattern = f"{self.KEY_PREFIX_STATS}:*"
            await self.redis.delete_pattern(pattern)
            
            logger.info("Invalidated all leaderboard caches")
        except Exception as e:
            logger.warning(f"Failed to invalidate caches: {e}")
    
    def get_current_period_key(self, scope: LeaderboardScope) -> str:
        """
        Generate period key for current time based on scope.
        
        Examples:
        - today: "2025-10-26"
        - weekly: "2025-W43"
        - alltime: "alltime"
        """
        now = datetime.now(timezone.utc)
        
        if scope == LeaderboardScope.TODAY:
            return now.strftime("%Y-%m-%d")
        elif scope == LeaderboardScope.WEEKLY:
            # ISO week format
            iso_calendar = now.isocalendar()
            return f"{iso_calendar.year}-W{iso_calendar.week:02d}"
        elif scope == LeaderboardScope.ALLTIME:
            return "alltime"
        
        raise ValueError(f"Invalid scope: {scope}")
    
    def get_cache_ttl(self, scope: LeaderboardScope) -> int:
        """Get cache TTL based on scope."""
        if scope == LeaderboardScope.TODAY:
            return self.CACHE_TTL_TODAY
        elif scope == LeaderboardScope.WEEKLY:
            return self.CACHE_TTL_WEEKLY
        elif scope == LeaderboardScope.ALLTIME:
            return self.CACHE_TTL_ALLTIME
        return self.CACHE_TTL_ALLTIME
    
    def _make_leaderboard_cache_key(self, scope: str, period_key: str, limit: int, offset: int) -> str:
        """Generate cache key for leaderboard."""
        return f"{self.KEY_PREFIX_LEADERBOARD}:{scope}:{period_key}:{limit}:{offset}"
    
    def _make_user_rank_cache_key(self, user_id: UUID, scope: str, period_key: str) -> str:
        """Generate cache key for user rank."""
        return f"{self.KEY_PREFIX_USER_RANK}:{user_id}:{scope}:{period_key}"
    
    def _make_stats_cache_key(self, scope: str, period_key: str) -> str:
        """Generate cache key for leaderboard stats."""
        return f"{self.KEY_PREFIX_STATS}:{scope}:{period_key}"
    
    async def get_leaderboard(
        self,
        scope: LeaderboardScope = LeaderboardScope.ALLTIME,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get leaderboard with caching.
        
        Returns:
            Dict with scope, period_key, total_participants, entries, and last_updated
        """
        period_key = self.get_current_period_key(scope)
        cache_key = self._make_leaderboard_cache_key(scope.value, period_key, limit, offset)
        
        # Try cache first
        cached_data = await self.redis.get_json(cache_key)
        if cached_data:
            return cached_data
        
        # Get from database
        scores = await self.repo.get_top_scores_for_period(scope, period_key, limit, offset)
        participants = await self.repo.count_participants_in_period(scope, period_key)
        
        # Format entries
        entries = []
        for idx, score_data in enumerate(scores):
            rank = offset + idx + 1
            
            # Extract data from aggregated result (dict from repository)
            user_id = score_data.get('user_id')
            user = score_data.get('user')
            total_score = int(score_data.get('total_score', 0))
            run_count = int(score_data.get('run_count', 0))
            
            # Safely access profile
            handle = "Anonymous"
            avatar_layers = {}
            
            if user and hasattr(user, 'profile') and user.profile:
                handle = user.profile.handle or "Anonymous"
                avatar_layers = user.profile.avatar_layers or {}
            
            entry = {
                "rank": rank,
                "user_id": str(user_id),
                "handle": handle,
                "score": total_score,
                "total_runs": run_count,
                "avatar_layers": avatar_layers,
            }
            entries.append(entry)
        
        # Build response
        leaderboard_data = {
            "scope": scope.value,
            "period_key": period_key,
            "total_participants": participants,
            "entries": entries,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache it
        cache_ttl = self.get_cache_ttl(scope)
        await self.redis.set_json(cache_key, leaderboard_data, cache_ttl)
        
        return leaderboard_data
    
    async def get_user_rank(
        self,
        user_id: UUID,
        scope: LeaderboardScope = LeaderboardScope.ALLTIME,
        neighbors_count: int = 3
    ) -> Dict[str, Any]:
        """
        Get user's rank and neighboring players.
        
        Returns:
            Dict with user_id, handle, rank, score, total_runs, scope, period_key, neighbors
        """
        period_key = self.get_current_period_key(scope)
        cache_key = self._make_user_rank_cache_key(user_id, scope.value, period_key)
        
        # Try cache first
        cached_data = await self.redis.get_json(cache_key)
        if cached_data:
            return cached_data
        
        # Get user's rank
        rank = await self.repo.get_user_rank_in_period(user_id, scope, period_key)
        
        if rank is None:
            # User has no scores in this period
            return {
                "user_id": str(user_id),
                "handle": "You",
                "rank": None,
                "score": 0,
                "total_runs": 0,
                "scope": scope.value,
                "period_key": period_key,
                "neighbors": []
            }
        
        # Get user score and neighbors
        user_score, neighbors = await self.repo.get_user_neighbors_in_leaderboard(
            user_id, scope, period_key, neighbors_count
        )
        
        # Format neighbors
        neighbor_entries = []
        for neighbor_score in neighbors:
            # Calculate neighbor rank (simplified - might not be exact)
            neighbor_rank = await self.repo.get_user_rank_in_period(
                neighbor_score.user_id, scope, period_key
            )
            
            neighbor_entries.append({
                "rank": neighbor_rank,
                "handle": neighbor_score.user.profile.handle if neighbor_score.user.profile else "Anonymous",
                "score": neighbor_score.score
            })
        
        # Sort neighbors by rank
        neighbor_entries.sort(key=lambda x: x["rank"] if x["rank"] else 999999)
        
        # Build response
        rank_data = {
            "user_id": str(user_id),
            "handle": user_score.user.profile.handle if user_score and user_score.user.profile else "You",
            "rank": rank,
            "score": user_score.score if user_score else 0,
            "total_runs": len([s for s in user_score.user.scores]) if user_score else 0,
            "scope": scope.value,
            "period_key": period_key,
            "neighbors": neighbor_entries
        }
        
        # Cache it
        cache_ttl = self.get_cache_ttl(scope)
        await self.redis.set_json(cache_key, rank_data, cache_ttl)
        
        return rank_data
    
    async def get_leaderboard_stats(
        self,
        scope: LeaderboardScope = LeaderboardScope.ALLTIME
    ) -> Dict[str, Any]:
        """
        Get leaderboard statistics with caching.
        
        Returns:
            Dict with scope, period_key, participants, total_scores, average_score,
            highest_score, lowest_score, last_updated
        """
        period_key = self.get_current_period_key(scope)
        cache_key = self._make_stats_cache_key(scope.value, period_key)
        
        # Try cache first
        cached_data = await self.redis.get_json(cache_key)
        if cached_data:
            return cached_data
        
        # Get from database
        stats = await self.repo.get_leaderboard_stats(scope, period_key)
        
        # Cache it
        cache_ttl = self.get_cache_ttl(scope)
        await self.redis.set_json(cache_key, stats, cache_ttl)
        
        return stats
    
    async def invalidate_leaderboard_cache(
        self,
        user_id: UUID,
        scope: Optional[LeaderboardScope] = None
    ) -> None:
        """
        Invalidate leaderboard cache when a new score is added.
        If scope is None, invalidate all scopes.
        """
        scopes_to_invalidate = (
            [scope] if scope else [LeaderboardScope.TODAY, LeaderboardScope.WEEKLY, LeaderboardScope.ALLTIME]
        )
        
        for scope_item in scopes_to_invalidate:
            period_key = self.get_current_period_key(scope_item)
            
            # Invalidate leaderboard cache (we'd need to iterate through common limit/offset combinations)
            # For simplicity, we'll invalidate common ones
            for limit in [10, 50, 100]:
                for offset in [0, 10, 50, 100]:
                    cache_key = self._make_leaderboard_cache_key(scope_item.value, period_key, limit, offset)
                    await self.redis.delete(cache_key)
            
            # Invalidate user rank cache
            user_rank_key = self._make_user_rank_cache_key(user_id, scope_item.value, period_key)
            await self.redis.delete(user_rank_key)
            
            # Invalidate stats cache
            stats_key = self._make_stats_cache_key(scope_item.value, period_key)
            await self.redis.delete(stats_key)
    
    async def update_user_score(
        self,
        user_id: UUID,
        score: int,
        run_id: UUID
    ) -> None:
        """
        Update user's score and invalidate relevant caches.
        This should be called after a run is completed.
        """
        # The score should already be in the database from run submission
        # We just need to invalidate caches
        await self.invalidate_leaderboard_cache(user_id)
    
    async def get_user_best_scores(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's best scores across different dungeons."""
        return await self.repo.get_user_best_scores_summary(user_id, limit)

