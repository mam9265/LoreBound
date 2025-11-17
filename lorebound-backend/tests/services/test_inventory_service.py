"""Tests for InventoryService."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch

from app.services.inventory_service import InventoryService
from app.services.exceptions import ItemNotFoundError, InventoryError


@pytest.mark.service
class TestInventoryService:
    """Test InventoryService functionality."""

    @pytest.fixture
    def inventory_service(self):
        """Create InventoryService instance."""
        return InventoryService()

    @pytest.mark.unit
    async def test_get_user_inventory_success(self, inventory_service, db_session, test_user):
        """Test successful inventory retrieval."""
        inventory_repo = Mock()
        inventory_repo.get_user_inventory = AsyncMock(return_value=[])
        inventory_repo.get_user_equipped_items = AsyncMock(return_value={})
        inventory_repo.calculate_equipped_stats = AsyncMock(return_value={})
        
        with patch('app.services.inventory_service.InventoryRepository', return_value=inventory_repo):
            result = await inventory_service.get_user_inventory(test_user.id, db_session)
            
            assert result is not None
            assert "items" in result
            assert "equipped" in result
            assert "stats" in result

    @pytest.mark.unit
    async def test_equip_item_success(self, inventory_service, db_session, test_user):
        """Test successful item equipping."""
        item_id = uuid4()
        inventory_repo = Mock()
        inventory_repo.get_item_by_id = AsyncMock(return_value=Mock(id=item_id))
        inventory_repo.user_owns_item = AsyncMock(return_value=True)
        inventory_repo.equip_item = AsyncMock(return_value=True)
        
        with patch('app.services.inventory_service.InventoryRepository', return_value=inventory_repo):
            result = await inventory_service.equip_item(
                user_id=test_user.id,
                item_id=item_id,
                slot="head",
                session=db_session
            )
            
            assert result is True

    @pytest.mark.unit
    async def test_equip_item_not_found(self, inventory_service, db_session, test_user):
        """Test equipping non-existent item."""
        item_id = uuid4()
        inventory_repo = Mock()
        inventory_repo.get_item_by_id = AsyncMock(return_value=None)
        
        with patch('app.services.inventory_service.InventoryRepository', return_value=inventory_repo):
            with pytest.raises(ItemNotFoundError):
                await inventory_service.equip_item(
                    user_id=test_user.id,
                    item_id=item_id,
                    slot="head",
                    session=db_session
                )

    @pytest.mark.unit
    async def test_equip_item_not_owned(self, inventory_service, db_session, test_user):
        """Test equipping item user doesn't own."""
        item_id = uuid4()
        inventory_repo = Mock()
        inventory_repo.get_item_by_id = AsyncMock(return_value=Mock(id=item_id))
        inventory_repo.user_owns_item = AsyncMock(return_value=False)
        
        with patch('app.services.inventory_service.InventoryRepository', return_value=inventory_repo):
            with pytest.raises(InventoryError):
                await inventory_service.equip_item(
                    user_id=test_user.id,
                    item_id=item_id,
                    slot="head",
                    session=db_session
                )

