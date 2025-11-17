"""Tests for RunService."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from app.services.run_service import RunService
from app.services.exceptions import InvalidRunDataError, AntiCheatViolationError, ScoreCalculationError
from app.domain.enums import RunStatus
from app.schemas.run import RunStartRequest, RunSubmitRequest


@pytest.mark.service
class TestRunService:
    """Test RunService functionality."""

    @pytest.fixture
    def run_service(self, mock_settings):
        """Create RunService instance."""
        return RunService(mock_settings)

    @pytest.mark.unit
    async def test_start_run_success(self, run_service, db_session, test_user):
        """Test successful run start."""
        dungeon_id = uuid4()
        run_repo = Mock()
        run_repo.create_run = AsyncMock(return_value=Mock(
            id=uuid4(),
            user_id=test_user.id,
            dungeon_id=dungeon_id,
            status=RunStatus.IN_PROGRESS
        ))
        
        with patch('app.services.run_service.RunRepository', return_value=run_repo):
            start_data = RunStartRequest(dungeon_id=dungeon_id)
            result = await run_service.start_run(test_user.id, start_data, db_session)
            
            assert result is not None
            assert result.run_id is not None

    @pytest.mark.unit
    async def test_submit_run_success(self, run_service, db_session, test_user):
        """Test successful run submission."""
        run_id = uuid4()
        run_repo = Mock()
        run_repo.get_run_by_id = AsyncMock(return_value=Mock(
            id=run_id,
            user_id=test_user.id,
            status=RunStatus.IN_PROGRESS,
            seed=12345
        ))
        run_repo.update_run_completion = AsyncMock()
        
        with patch('app.services.run_service.RunRepository', return_value=run_repo):
            submit_data = RunSubmitRequest(
                signature="valid_signature",
                turns=[],
                total_time_ms=60000
            )
            result = await run_service.submit_run(test_user.id, run_id, submit_data, db_session)
            
            assert result is not None

    @pytest.mark.unit
    async def test_submit_run_not_found(self, run_service, db_session, test_user):
        """Test submitting non-existent run."""
        run_id = uuid4()
        run_repo = Mock()
        run_repo.get_run_by_id = AsyncMock(return_value=None)
        
        with patch('app.services.run_service.RunRepository', return_value=run_repo):
            submit_data = RunSubmitRequest(
                signature="signature",
                turns=[],
                total_time_ms=60000
            )
            
            with pytest.raises(InvalidRunDataError):
                await run_service.submit_run(test_user.id, run_id, submit_data, db_session)

    @pytest.mark.unit
    async def test_submit_run_wrong_user(self, run_service, db_session, test_user):
        """Test submitting run belonging to different user."""
        run_id = uuid4()
        other_user_id = uuid4()
        run_repo = Mock()
        run_repo.get_run_by_id = AsyncMock(return_value=Mock(
            id=run_id,
            user_id=other_user_id,
            status=RunStatus.IN_PROGRESS
        ))
        
        with patch('app.services.run_service.RunRepository', return_value=run_repo):
            submit_data = RunSubmitRequest(
                signature="signature",
                turns=[],
                total_time_ms=60000
            )
            
            with pytest.raises(InvalidRunDataError):
                await run_service.submit_run(test_user.id, run_id, submit_data, db_session)

