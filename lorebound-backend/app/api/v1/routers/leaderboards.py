"""Leaderboard endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@router.get("/")
async def get_leaderboard():
    """Get leaderboard for specified scope."""
    pass


@router.get("/me")
async def get_my_rank():
    """Get current user's rank and neighbors."""
    pass
