"""Inventory and item schemas."""

from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..domain.enums import ItemSlot, ItemRarity


class ItemResponse(BaseModel):
    """Item response schema."""
    id: UUID = Field(..., description="Item unique identifier")
    slug: str = Field(..., description="Item slug identifier")
    name: str = Field(..., description="Item display name")
    slot: ItemSlot = Field(..., description="Equipment slot")
    rarity: ItemRarity = Field(..., description="Item rarity")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Item statistics")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "slug": "legendary_sword_of_wisdom",
                "name": "Legendary Sword of Wisdom",
                "slot": "weapon",
                "rarity": "legendary",
                "stats": {
                    "attack": 150,
                    "intellect": 75,
                    "critical_chance": 0.15
                }
            }
        }
    )


class InventoryItemResponse(BaseModel):
    """Inventory item response schema."""
    item: ItemResponse = Field(..., description="Item details")
    equipped: bool = Field(..., description="Whether item is currently equipped")
    acquired_at: datetime = Field(..., description="When item was acquired")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "item": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "slug": "legendary_sword_of_wisdom",
                    "name": "Legendary Sword of Wisdom",
                    "slot": "weapon",
                    "rarity": "legendary",
                    "stats": {
                        "attack": 150,
                        "intellect": 75,
                        "critical_chance": 0.15
                    }
                },
                "equipped": True,
                "acquired_at": "2024-01-01T10:00:00Z"
            }
        }
    )


class InventoryResponse(BaseModel):
    """Complete inventory response schema."""
    items: List[InventoryItemResponse] = Field(..., description="User's inventory items")
    equipped_items: Dict[ItemSlot, ItemResponse] = Field(default_factory=dict, description="Currently equipped items by slot")
    total_items: int = Field(..., description="Total number of items in inventory")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "item": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "slug": "legendary_sword_of_wisdom",
                            "name": "Legendary Sword of Wisdom",
                            "slot": "weapon",
                            "rarity": "legendary",
                            "stats": {"attack": 150, "intellect": 75}
                        },
                        "equipped": True,
                        "acquired_at": "2024-01-01T10:00:00Z"
                    }
                ],
                "equipped_items": {
                    "weapon": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "slug": "legendary_sword_of_wisdom",
                        "name": "Legendary Sword of Wisdom",
                        "slot": "weapon",
                        "rarity": "legendary",
                        "stats": {"attack": 150, "intellect": 75}
                    }
                },
                "total_items": 25
            }
        }
    )


class EquipItemRequest(BaseModel):
    """Equip item request schema."""
    item_id: UUID = Field(..., description="Item identifier to equip")
    slot: ItemSlot = Field(..., description="Equipment slot")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "123e4567-e89b-12d3-a456-426614174000",
                "slot": "weapon"
            }
        }
    )


class EquipItemResponse(BaseModel):
    """Equip item response schema."""
    success: bool = Field(..., description="Whether equip operation succeeded")
    equipped_item: ItemResponse = Field(..., description="Newly equipped item")
    previous_item: Optional[ItemResponse] = Field(None, description="Previously equipped item in this slot")
    updated_stats: Dict[str, Any] = Field(default_factory=dict, description="Updated character stats")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "equipped_item": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "slug": "legendary_sword_of_wisdom",
                    "name": "Legendary Sword of Wisdom",
                    "slot": "weapon",
                    "rarity": "legendary",
                    "stats": {"attack": 150, "intellect": 75}
                },
                "previous_item": None,
                "updated_stats": {
                    "total_attack": 200,
                    "total_intellect": 125,
                    "total_critical_chance": 0.25
                }
            }
        }
    )
