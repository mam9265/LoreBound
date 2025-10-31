"""Game run endpoints."""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_active_user
from ....services.dependencies import get_run_service_with_session
from ....services.run_service import RunService
from ....services.exceptions import (
    InvalidRunDataError,
    AntiCheatViolationError,
    ScoreCalculationError
)
from ....schemas.run import (
    RunStartRequest,
    RunSubmitRequest,
    RunResponse,
    RunStatsResponse
)
from ....domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/start", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def start_run(
    start_data: RunStartRequest,
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> RunResponse:
    """
    Start a new game run.
    
    Creates a new game session with anti-cheat token for the specified dungeon.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Starting run for user {current_user.id}, dungeon {start_data.dungeon_id}")
        result = await run_service.start_run(current_user.id, start_data, session)
        await session.commit()
        logger.info(f"Run started successfully: {result.id}")
        return result
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to start run for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start run: {str(e)}"
        )


@router.post("/{run_id}/validate-answer")
async def validate_answer(
    run_id: UUID,
    question_id: UUID,
    answer_index: int,
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate a single answer for real-time feedback.
    
    Returns whether the answer was correct without completing the run.
    """
    run_service, session = service_session
    
    try:
        from ....repositories.content_repo import ContentRepository
        content_repo = ContentRepository(session)
        
        # Get the question
        question = await content_repo.get_question_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Validate the run belongs to user
        run = await run_service.run_repo.get_run_by_id(run_id)
        if not run or run.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found"
            )
        
        # Check if answer is correct
        is_correct = answer_index == question.answer_index
        
        return {
            "is_correct": is_correct,
            "correct_answer_index": question.answer_index if not is_correct else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate answer"
        )


@router.post("/{run_id}/submit", response_model=RunResponse)
async def submit_run(
    run_id: UUID,
    submit_data: RunSubmitRequest,
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> RunResponse:
    """
    Submit completed run with anti-cheat verification.
    
    Validates run data, calculates scores, and updates user progression.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Submitting run {run_id} for user {current_user.id}")
        result = await run_service.submit_run(current_user.id, run_id, submit_data, session)
        await session.commit()
        
        # Invalidate leaderboard caches so new score appears immediately
        try:
            from ....core.redis_client import get_redis
            from ....services.leaderboard_service import LeaderboardService
            redis = await anext(get_redis())
            lb_service = LeaderboardService(session, redis)
            await lb_service.invalidate_all_caches()
            logger.info("Invalidated leaderboard caches after run submission")
        except Exception as cache_error:
            logger.warning(f"Failed to invalidate leaderboard cache: {cache_error}")
        
        logger.info(f"Run submitted successfully: {run_id}")
        return result
        
    except InvalidRunDataError as e:
        await session.rollback()
        logger.warning(f"Invalid run data for {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AntiCheatViolationError as e:
        await session.rollback()
        logger.warning(f"Anti-cheat violation for run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Anti-cheat violation: {str(e)}"
        )
    except ScoreCalculationError as e:
        await session.rollback()
        logger.warning(f"Score calculation error for run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score calculation error: {str(e)}"
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to submit run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit run"
        )


@router.get("/", response_model=List[RunResponse])
async def get_user_runs(
    limit: int = Query(default=20, ge=1, le=100, description="Number of runs to return"),
    offset: int = Query(default=0, ge=0, description="Number of runs to skip"),
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> List[RunResponse]:
    """
    Get user's run history.
    
    Returns paginated list of user's game runs ordered by most recent first.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Fetching runs for user {current_user.id}, limit={limit}, offset={offset}")
        runs = await run_service.get_user_runs(current_user.id, limit, offset, session)
        logger.info(f"Retrieved {len(runs)} runs for user {current_user.id}")
        return runs
        
    except Exception as e:
        logger.error(f"Failed to fetch runs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch runs"
        )


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: UUID,
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> RunResponse:
    """
    Get specific run details.
    
    Returns detailed information about a specific run including scores and metadata.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Fetching run {run_id} for user {current_user.id}")
        run = await run_service.get_run_by_id(current_user.id, run_id, session)
        logger.info(f"Retrieved run {run_id} for user {current_user.id}")
        return run
        
    except InvalidRunDataError as e:
        logger.warning(f"Run access denied for {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to fetch run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch run"
        )


@router.post("/{run_id}/abandon", response_model=RunResponse)
async def abandon_run(
    run_id: UUID,
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> RunResponse:
    """
    Abandon a run in progress.
    
    Marks the run as abandoned and prevents further submission.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Abandoning run {run_id} for user {current_user.id}")
        result = await run_service.abandon_run(current_user.id, run_id, session)
        logger.info(f"Run abandoned: {run_id}")
        return result
        
    except InvalidRunDataError as e:
        logger.warning(f"Cannot abandon run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to abandon run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to abandon run"
        )


@router.get("/stats/me", response_model=RunStatsResponse)
async def get_user_stats(
    service_session: tuple[RunService, AsyncSession] = Depends(get_run_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> RunStatsResponse:
    """
    Get user's game statistics.
    
    Returns comprehensive statistics about user's game performance.
    """
    run_service, session = service_session
    
    try:
        logger.info(f"Fetching stats for user {current_user.id}")
        stats = await run_service.get_user_stats(current_user.id, session)
        logger.info(f"Retrieved stats for user {current_user.id}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to fetch stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stats"
        )
