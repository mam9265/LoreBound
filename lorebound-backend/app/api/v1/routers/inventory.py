"""Inventory and item management endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/")
async def get_inventory():
    """Get user inventory."""
    pass


@router.post("/equip")
async def equip_item():
    """Equip an item."""
    pass
