"""Configuration and feature flags endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/")
async def get_config():
    """Get game configuration and feature flags."""
    pass
