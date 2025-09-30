"""Run service for managing game sessions and scoring."""

import logging
import hashlib
import hmac
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings
from ..domain.enums import RunStatus
from ..domain.models import Run
from ..repositories.run_repo import RunRepository
from ..repositories.user_repo import UserRepository
from ..schemas.run import (
    RunStartRequest,
    RunSubmitRequest,
    RunResponse,
    ScoreResponse,
    RunStatsResponse
)
from .exceptions import (
    RunServiceError,
    InvalidRunDataError,
    AntiCheatViolationError,
    ScoreCalculationError
)

logger = logging.getLogger(__name__)


class RunService:
    """Service for handling game run operations."""

    def __init__(
        self,
        run_repo: RunRepository,
        user_repo: UserRepository,
        settings: Settings
    ):
        self.run_repo = run_repo
        self.user_repo = user_repo
        self.settings = settings

    async def start_run(
        self,
        user_id: UUID,
        start_data: RunStartRequest,
        session: AsyncSession
    ) -> RunResponse:
        """
        Start a new game run for a user.
        
        Creates a new run with anti-cheat signature and returns run details.
        """
        logger.info(f"Starting run for user {user_id}, dungeon {start_data.dungeon_id}")

        try:
            # Generate anti-cheat session token
            session_token = self._generate_session_token(user_id, start_data.dungeon_id)
            
            # Create run
            run = await self.run_repo.create_run(
                user_id=user_id,
                dungeon_id=start_data.dungeon_id,
                floor=start_data.floor,
                session_token=session_token,
                client_metadata=start_data.client_metadata,
                session=session
            )

            logger.info(f"Run started: {run.id} for user {user_id}")
            return RunResponse.model_validate(run)

        except Exception as e:
            logger.error(f"Failed to start run for user {user_id}: {e}")
            raise RunServiceError(f"Failed to start run: {e}")

    async def submit_run(
        self,
        user_id: UUID,
        run_id: UUID,
        submit_data: RunSubmitRequest,
        session: AsyncSession
    ) -> RunResponse:
        """
        Submit a completed game run with anti-cheat validation.
        
        Validates run data, calculates scores, and updates user progression.
        """
        logger.info(f"Submitting run {run_id} for user {user_id}")

        try:
            # Get existing run
            run = await self.run_repo.get_by_id(run_id, session)
            if not run:
                raise InvalidRunDataError(f"Run not found: {run_id}")
            
            if run.user_id != user_id:
                raise InvalidRunDataError("Run does not belong to user")
            
            if run.status != RunStatus.IN_PROGRESS:
                raise InvalidRunDataError(f"Run is not in progress: {run.status}")

            # Validate anti-cheat signature
            await self._validate_run_signature(run, submit_data)

            # Calculate and validate scores
            validated_scores = await self._calculate_and_validate_scores(
                run, submit_data, session
            )

            # Update run with results
            updated_run = await self.run_repo.complete_run(
                run_id=run_id,
                scores=validated_scores,
                total_score=sum(score.points for score in validated_scores),
                client_signature=submit_data.client_signature,
                session=session
            )

            # Update user progression if needed
            await self._update_user_progression(user_id, updated_run, session)

            logger.info(f"Run submitted successfully: {run_id} for user {user_id}")
            return RunResponse.model_validate(updated_run)

        except (InvalidRunDataError, AntiCheatViolationError, ScoreCalculationError):
            raise
        except Exception as e:
            logger.error(f"Failed to submit run {run_id} for user {user_id}: {e}")
            raise RunServiceError(f"Failed to submit run: {e}")

    async def get_user_runs(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        session: AsyncSession = None
    ) -> List[RunResponse]:
        """Get user's run history."""
        logger.info(f"Fetching runs for user {user_id}, limit={limit}, offset={offset}")

        try:
            runs = await self.run_repo.get_user_runs(
                user_id=user_id,
                limit=limit,
                offset=offset,
                session=session
            )

            return [RunResponse.model_validate(run) for run in runs]

        except Exception as e:
            logger.error(f"Failed to fetch runs for user {user_id}: {e}")
            raise RunServiceError(f"Failed to fetch runs: {e}")

    async def get_run_by_id(
        self,
        user_id: UUID,
        run_id: UUID,
        session: AsyncSession
    ) -> RunResponse:
        """Get specific run details."""
        logger.info(f"Fetching run {run_id} for user {user_id}")

        try:
            run = await self.run_repo.get_by_id(run_id, session)
            if not run:
                raise InvalidRunDataError(f"Run not found: {run_id}")
            
            if run.user_id != user_id:
                raise InvalidRunDataError("Run does not belong to user")

            return RunResponse.model_validate(run)

        except InvalidRunDataError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch run {run_id}: {e}")
            raise RunServiceError(f"Failed to fetch run: {e}")

    async def get_user_stats(
        self,
        user_id: UUID,
        session: AsyncSession
    ) -> RunStatsResponse:
        """Get user's game statistics."""
        logger.info(f"Fetching stats for user {user_id}")

        try:
            stats = await self.run_repo.get_user_statistics(user_id, session)
            return RunStatsResponse.model_validate(stats)

        except Exception as e:
            logger.error(f"Failed to fetch stats for user {user_id}: {e}")
            raise RunServiceError(f"Failed to fetch stats: {e}")

    def _generate_session_token(self, user_id: UUID, dungeon_id: UUID) -> str:
        """Generate anti-cheat session token for run."""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        data = f"{user_id}:{dungeon_id}:{timestamp}:{self.settings.feature_flags_seed}"
        
        signature = hmac.new(
            key=self.settings.jwt_private_key.encode()[:32],  # Use first 32 bytes
            msg=data.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"

    async def _validate_run_signature(
        self,
        run: Run,
        submit_data: RunSubmitRequest
    ) -> None:
        """Validate anti-cheat signature for run submission."""
        if not submit_data.client_signature:
            raise AntiCheatViolationError("Missing client signature")

        # Extract timestamp from session token
        try:
            token_timestamp = int(run.session_token.split(':')[0])
        except (ValueError, IndexError):
            raise AntiCheatViolationError("Invalid session token format")

        # Validate run duration (reasonable time bounds)
        now = datetime.now(timezone.utc)
        run_duration = (now - run.started_at).total_seconds()
        
        # Basic time validation (min 30 seconds, max 1 hour per run)
        if run_duration < 30:
            raise AntiCheatViolationError("Run completed too quickly")
        if run_duration > 3600:
            raise AntiCheatViolationError("Run took too long")

        # Validate turn count matches submitted scores
        if len(submit_data.turn_data) != len(submit_data.scores):
            raise AntiCheatViolationError("Turn data count doesn't match score count")

        logger.info(f"Anti-cheat validation passed for run {run.id}")

    async def _calculate_and_validate_scores(
        self,
        run: Run,
        submit_data: RunSubmitRequest,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Calculate and validate scores for run submission."""
        validated_scores = []

        try:
            for i, (turn, score_data) in enumerate(zip(submit_data.turn_data, submit_data.scores)):
                # Basic score validation
                if score_data.points < 0:
                    raise ScoreCalculationError(f"Negative score not allowed: turn {i}")
                
                if score_data.points > 1000:  # Max points per question
                    raise ScoreCalculationError(f"Score too high: turn {i}")

                # Validate answer time (reasonable bounds)
                if score_data.answer_time < 0.5:  # Min half second
                    raise ScoreCalculationError(f"Answer time too fast: turn {i}")
                
                if score_data.answer_time > 60:  # Max 1 minute per question
                    raise ScoreCalculationError(f"Answer time too slow: turn {i}")

                # Create validated score entry
                validated_score = {
                    "question_index": i,
                    "points": score_data.points,
                    "answer_time": score_data.answer_time,
                    "is_correct": score_data.is_correct,
                    "streak_bonus": score_data.streak_bonus,
                    "time_bonus": score_data.time_bonus
                }
                
                validated_scores.append(validated_score)

            return validated_scores

        except ScoreCalculationError:
            raise
        except Exception as e:
            logger.error(f"Score calculation error: {e}")
            raise ScoreCalculationError(f"Score calculation failed: {e}")

    async def _update_user_progression(
        self,
        user_id: UUID,
        run: Run,
        session: AsyncSession
    ) -> None:
        """Update user progression based on run results."""
        try:
            # Calculate XP gained (basic formula)
            xp_gained = min(run.total_score // 10, 500)  # 1 XP per 10 points, max 500
            
            if xp_gained > 0:
                await self.user_repo.add_experience(user_id, xp_gained, session)
                logger.info(f"Added {xp_gained} XP to user {user_id}")

        except Exception as e:
            logger.warning(f"Failed to update user progression: {e}")
            # Don't fail the run submission if progression update fails

    async def abandon_run(
        self,
        user_id: UUID,
        run_id: UUID,
        session: AsyncSession
    ) -> RunResponse:
        """Abandon a run in progress."""
        logger.info(f"Abandoning run {run_id} for user {user_id}")

        try:
            run = await self.run_repo.get_by_id(run_id, session)
            if not run:
                raise InvalidRunDataError(f"Run not found: {run_id}")
            
            if run.user_id != user_id:
                raise InvalidRunDataError("Run does not belong to user")
            
            if run.status != RunStatus.IN_PROGRESS:
                raise InvalidRunDataError(f"Run is not in progress: {run.status}")

            # Mark run as abandoned
            updated_run = await self.run_repo.abandon_run(run_id, session)
            
            logger.info(f"Run abandoned: {run_id} for user {user_id}")
            return RunResponse.model_validate(updated_run)

        except InvalidRunDataError:
            raise
        except Exception as e:
            logger.error(f"Failed to abandon run {run_id}: {e}")
            raise RunServiceError(f"Failed to abandon run: {e}")


# Dependency for getting run service
def get_run_service(
    run_repo: RunRepository,
    user_repo: UserRepository,
    settings: Settings
) -> RunService:
    """Dependency to get run service."""
    return RunService(run_repo, user_repo, settings)
