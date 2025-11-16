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
    RunStatsResponse,
    StartRunResponse,
    ItemBonusResponse
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
    ) -> StartRunResponse:
        """
        Start a new game run for a user.
        
        Creates a new run with anti-cheat signature and returns run details including equipped item bonuses.
        """
        logger.info(f"Starting run for user {user_id}, dungeon {start_data.dungeon_id}")

        try:
            # Generate seed for this run
            import random
            import time
            seed = int(time.time() * 1000) % 1000000
            
            # Generate anti-cheat session token
            session_token = self._generate_session_token(user_id, start_data.dungeon_id)
            
            # Load user's equipped items
            from ..repositories.inventory_repo import InventoryRepository
            inventory_repo = InventoryRepository(session)
            equipped_items_dict = await inventory_repo.get_user_equipped_items(user_id)
            
            # Convert equipped items to ItemBonusResponse and calculate total bonuses
            equipped_items = []
            total_bonuses = {}
            
            for slot, item in equipped_items_dict.items():
                # Create item response
                item_response = ItemBonusResponse(
                    item_id=item.id,
                    name=item.name,
                    slot=item.slot.value if hasattr(item.slot, 'value') else str(item.slot),
                    rarity=item.rarity.value if hasattr(item.rarity, 'value') else str(item.rarity),
                    stats=item.stats or {}
                )
                equipped_items.append(item_response)
                
                # Accumulate bonuses
                for stat_name, stat_value in (item.stats or {}).items():
                    if isinstance(stat_value, (int, float)):
                        # For multipliers (e.g., score_multiplier), multiply them together
                        if 'multiplier' in stat_name:
                            total_bonuses[stat_name] = total_bonuses.get(stat_name, 1.0) * stat_value
                        else:
                            # For additive bonuses (e.g., time_extension), add them
                            total_bonuses[stat_name] = total_bonuses.get(stat_name, 0) + stat_value
            
            logger.info(f"User {user_id} has {len(equipped_items)} equipped items with bonuses: {total_bonuses}")
            
            # Create run
            run = await self.run_repo.create_run(
                user_id=user_id,
                dungeon_id=start_data.dungeon_id,
                seed=seed,
                floor=start_data.floor,
                session_token=session_token,
                summary={
                    "client_metadata": start_data.client_metadata,
                    "equipped_items": [{"id": str(item.item_id), "name": item.name} for item in equipped_items],
                    "total_bonuses": total_bonuses
                }
            )

            logger.info(f"Run started: {run.id} for user {user_id}")
            
            # Return StartRunResponse with item bonuses
            return StartRunResponse(
                run_id=run.id,
                seed=seed,
                session_token=session_token,
                dungeon_id=start_data.dungeon_id,
                floor=start_data.floor,
                equipped_items=equipped_items,
                total_bonuses=total_bonuses
            )

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
            run = await self.run_repo.get_run_by_id(run_id)
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

            # Calculate total score
            total_score = sum(score["points"] for score in validated_scores)
            
            # Calculate stats for leaderboard
            correct_count = sum(1 for score in validated_scores if score["is_correct"])
            total_time_ms = sum(int(score["answer_time"] * 1000) for score in validated_scores)
            streak_max = max((score.get("streak_bonus", 0) for score in validated_scores), default=0)
            
            # Update run with results
            updated_run = await self.run_repo.complete_run(
                run_id=run_id,
                total_score=total_score,
                summary={
                    "scores": validated_scores,
                    "client_signature": submit_data.client_signature
                },
                signature=submit_data.client_signature
            )

            # Create Score record for leaderboard
            from ..domain.models import Score
            score_record = Score(
                run_id=run_id,
                user_id=user_id,
                floor=run.floor,
                correct_count=correct_count,
                total_time_ms=total_time_ms,
                streak_max=streak_max,
                score=total_score
            )
            session.add(score_record)
            await session.flush()
            logger.info(f"Created score record for run {run_id}: {total_score} points")

            # Invalidate leaderboard cache (will be refreshed on next request)
            # Note: We could import LeaderboardService here if needed for cache invalidation
            # For now, cache will expire naturally (30s-5min TTL)

            # Update user progression if needed
            await self._update_user_progression(user_id, updated_run, session)

            # Distribute item rewards for completing the run
            from .inventory_service import InventoryService
            inventory_service = InventoryService()
            
            # Use getattr with defaults for backward compatibility
            is_daily = getattr(submit_data, 'is_daily_challenge', False)
            is_victory = getattr(submit_data, 'is_victory', True)
            
            try:
                rewards = await inventory_service.distribute_run_rewards(
                    user_id=user_id,
                    is_daily_challenge=is_daily,
                    is_victory=is_victory,
                    score=total_score,
                    session=session
                )
                
                # Add rewards to the run response summary
                if updated_run.summary is None:
                    updated_run.summary = {}
                updated_run.summary["rewards"] = rewards
                logger.info(f"Distributed {len(rewards)} rewards to user {user_id} for run {run_id}")
            except Exception as e:
                logger.error(f"Failed to distribute rewards for run {run_id}: {e}")
                # Don't fail the run submission if rewards fail
                updated_run.summary = updated_run.summary or {}
                updated_run.summary["rewards"] = []

            # Fetch the updated run with dungeon relationship
            final_run = await self.run_repo.get_run_by_id(run_id)
            
            logger.info(f"Run submitted successfully: {run_id} for user {user_id}")
            
            # Manually create response with dungeon data
            from ..schemas.content import DungeonMetaResponse
            run_dict = {
                'id': final_run.id,
                'user_id': final_run.user_id,
                'dungeon_id': final_run.dungeon_id,
                'floor': final_run.floor,
                'status': final_run.status,
                'session_token': final_run.session_token,
                'total_score': final_run.total_score,
                'started_at': final_run.started_at,
                'completed_at': final_run.completed_at,
                'dungeon': DungeonMetaResponse.model_validate(final_run.dungeon) if final_run.dungeon else None
            }
            return RunResponse(**run_dict)

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
                offset=offset
            )

            # Convert runs to response objects
            from ..schemas.content import DungeonMetaResponse
            responses = []
            for run in runs:
                # Manually create response with dungeon data
                run_dict = {
                    'id': run.id,
                    'user_id': run.user_id,
                    'dungeon_id': run.dungeon_id,
                    'floor': run.floor,
                    'status': run.status,
                    'session_token': run.session_token,
                    'total_score': run.total_score,
                    'started_at': run.started_at,
                    'completed_at': run.completed_at,
                    'dungeon': DungeonMetaResponse.model_validate(run.dungeon) if run.dungeon else None
                }
                responses.append(RunResponse(**run_dict))
            
            return responses

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
            run = await self.run_repo.get_run_by_id(run_id)
            if not run:
                raise InvalidRunDataError(f"Run not found: {run_id}")
            
            if run.user_id != user_id:
                raise InvalidRunDataError("Run does not belong to user")

            # Manually create response with dungeon data
            from ..schemas.content import DungeonMetaResponse
            run_dict = {
                'id': run.id,
                'user_id': run.user_id,
                'dungeon_id': run.dungeon_id,
                'floor': run.floor,
                'status': run.status,
                'session_token': run.session_token,
                'total_score': run.total_score,
                'started_at': run.started_at,
                'completed_at': run.completed_at,
                'dungeon': DungeonMetaResponse.model_validate(run.dungeon) if run.dungeon else None
            }
            return RunResponse(**run_dict)

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
            stats = await self.run_repo.get_user_statistics(user_id)
            return RunStatsResponse(**stats)

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
        
        # Basic time validation (min 1 second to prevent instant submission, max 1 hour per run)
        if run_duration < 1:
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
                # Allow very fast answers (0.1s minimum) - players can be quick!
                if score_data.answer_time < 0.1:  # Min 0.1 second (not instant)
                    raise ScoreCalculationError(f"Answer time too fast: turn {i}")
                
                if score_data.answer_time > 90:  # Max 90 seconds (accounting for time extensions)
                    raise ScoreCalculationError(f"Answer time too slow: turn {i}")

                # Create validated score entry (includes item bonus from equipped items)
                validated_score = {
                    "question_index": i,
                    "points": score_data.points,
                    "answer_time": score_data.answer_time,
                    "is_correct": score_data.is_correct,
                    "streak_bonus": score_data.streak_bonus,
                    "time_bonus": score_data.time_bonus,
                    "item_bonus": score_data.item_bonus
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
            run = await self.run_repo.get_run_by_id(run_id)
            if not run:
                raise InvalidRunDataError(f"Run not found: {run_id}")
            
            if run.user_id != user_id:
                raise InvalidRunDataError("Run does not belong to user")
            
            if run.status != RunStatus.IN_PROGRESS:
                raise InvalidRunDataError(f"Run is not in progress: {run.status}")

            # Mark run as abandoned
            await self.run_repo.abandon_run(run_id)
            
            # Fetch the updated run with dungeon relationship
            updated_run = await self.run_repo.get_run_by_id(run_id)
            
            logger.info(f"Run abandoned: {run_id} for user {user_id}")
            
            # Manually create response with dungeon data
            from ..schemas.content import DungeonMetaResponse
            run_dict = {
                'id': updated_run.id,
                'user_id': updated_run.user_id,
                'dungeon_id': updated_run.dungeon_id,
                'floor': updated_run.floor,
                'status': updated_run.status,
                'session_token': updated_run.session_token,
                'total_score': updated_run.total_score,
                'started_at': updated_run.started_at,
                'completed_at': updated_run.completed_at,
                'dungeon': DungeonMetaResponse.model_validate(updated_run.dungeon) if updated_run.dungeon else None
            }
            return RunResponse(**run_dict)

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
