"""Leaderboard endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_active_user
from ....core.redis_client import get_redis, RedisClient
from ....repositories.base import get_session
from ....domain.models import User
from ....domain.enums import LeaderboardScope
from ....services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@router.get("/")
async def get_leaderboard(
    scope: LeaderboardScope = Query(default=LeaderboardScope.ALLTIME, description="Time scope for leaderboard"),
    limit: int = Query(default=100, ge=1, le=100, description="Number of entries to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis),
):
    """
    Get leaderboard rankings for the specified scope.
    
    **Scopes:**
    - `today`: Rankings for today
    - `weekly`: Rankings for current week
    - `alltime`: All-time rankings
    
    **Response:**
    - `scope`: The requested scope
    - `period_key`: Period identifier (e.g., "2025-10-26" for today)
    - `total_participants`: Total number of players with scores in this period
    - `entries`: List of leaderboard entries with rank, handle, score, etc.
    - `last_updated`: Timestamp of when this data was generated
    """
    service = LeaderboardService(session, redis)
    
    try:
        leaderboard_data = await service.get_leaderboard(scope, limit, offset)
        return leaderboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard: {str(e)}"
        )


@router.get("/me")
async def get_my_rank(
    scope: LeaderboardScope = Query(default=LeaderboardScope.ALLTIME, description="Time scope for ranking"),
    neighbors: int = Query(default=3, ge=0, le=10, description="Number of neighbors to show"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis),
):
    """
    Get current user's rank and neighboring players.
    
    **Scopes:**
    - `today`: Your rank for today
    - `weekly`: Your rank for current week
    - `alltime`: Your all-time rank
    
    **Response:**
    - `user_id`: Your user ID
    - `handle`: Your handle
    - `rank`: Your current rank (null if no scores in this period)
    - `score`: Your score for this period
    - `total_runs`: Your total number of runs
    - `scope`: The requested scope
    - `period_key`: Period identifier
    - `neighbors`: List of players ranked near you
    """
    service = LeaderboardService(session, redis)
    
    try:
        rank_data = await service.get_user_rank(
            user_id=current_user.id,
            scope=scope,
            neighbors_count=neighbors
        )
        return rank_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user rank: {str(e)}"
        )


@router.get("/stats")
async def get_leaderboard_stats(
    scope: LeaderboardScope = Query(default=LeaderboardScope.ALLTIME, description="Time scope for statistics"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis),
):
    """
    Get leaderboard statistics for the specified scope.
    
    **Scopes:**
    - `today`: Statistics for today
    - `weekly`: Statistics for current week
    - `alltime`: All-time statistics
    
    **Response:**
    - `scope`: The requested scope
    - `period_key`: Period identifier
    - `participants`: Number of unique participants
    - `total_scores`: Total number of scores recorded
    - `average_score`: Average score across all participants
    - `highest_score`: Highest score in this period
    - `lowest_score`: Lowest score in this period
    - `last_updated`: Timestamp of when this data was generated
    """
    service = LeaderboardService(session, redis)
    
    try:
        stats = await service.get_leaderboard_stats(scope)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard stats: {str(e)}"
        )
