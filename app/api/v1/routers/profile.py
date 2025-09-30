"""User profile endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/")
async def get_profile():
    """Get user profile."""
    pass


@router.put("/")
async def update_profile():
    """Update user profile."""
    pass
