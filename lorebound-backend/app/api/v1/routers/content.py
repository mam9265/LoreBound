"""Content endpoints for dungeons, questions, and daily challenges."""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_active_user
from ....services.dependencies import get_content_service_with_session
from ....services.content_service import ContentService
from ....services.exceptions import (
    DungeonNotFoundError,
    ContentError,
    DailyChallengeError
)
from ....schemas.content import (
    DungeonResponse,
    QuestionResponse,
    DailyChallengeResponse,
    QuestionsRequest,
    QuestionsResponse
)
from ....domain.models import User, DailyChallenge

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content", tags=["content"])


@router.get("/dungeons", response_model=List[DungeonResponse])
async def get_dungeons(
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> List[DungeonResponse]:
    """
    Get all available dungeons.
    
    Returns list of dungeons available for the authenticated user to play.
    """
    content_service, session = service_session
    
    try:
        logger.info(f"Fetching dungeons for user: {current_user.id}")
        dungeons = await content_service.get_available_dungeons(session)
        logger.info(f"Retrieved {len(dungeons)} dungeons for user: {current_user.id}")
        return dungeons
        
    except Exception as e:
        logger.error(f"Failed to fetch dungeons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dungeons"
        )


@router.get("/dungeons/{dungeon_id}", response_model=DungeonResponse)
async def get_dungeon(
    dungeon_id: UUID,
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> DungeonResponse:
    """
    Get specific dungeon details.
    
    Returns detailed information about a specific dungeon including tiers and metadata.
    """
    content_service, session = service_session
    
    try:
        logger.info(f"Fetching dungeon {dungeon_id} for user: {current_user.id}")
        dungeon = await content_service.get_dungeon_by_id(dungeon_id, session)
        logger.info(f"Retrieved dungeon {dungeon_id} for user: {current_user.id}")
        return dungeon
        
    except DungeonNotFoundError:
        logger.warning(f"Dungeon not found: {dungeon_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dungeon not found: {dungeon_id}"
        )
    except Exception as e:
        logger.error(f"Failed to fetch dungeon {dungeon_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dungeon"
        )


@router.get("/questions", response_model=QuestionsResponse)
async def get_questions(
    dungeon_id: UUID = Query(..., description="Dungeon ID to get questions for"),
    floor: int = Query(..., ge=1, le=100, description="Floor number"),
    count: int = Query(default=10, ge=1, le=50, description="Number of questions"),
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> QuestionsResponse:
    """
    Get questions for a dungeon with varied selection.
    
    Returns a different set of questions for each request, providing variety across runs.
    """
    content_service, session = service_session
    
    try:
        import time
        # Generate unique seed for this request to ensure variety
        run_seed = int(time.time() * 1000000) % (2**31)
        
        logger.info(f"Fetching {count} questions for user {current_user.id}, dungeon {dungeon_id}, floor {floor}, seed {run_seed}")
        
        questions = await content_service.get_questions_for_dungeon(
            dungeon_id=dungeon_id,
            floor=floor,
            count=count,
            user_id=current_user.id,
            session=session,
            run_seed=run_seed
        )
        
        response = QuestionsResponse(
            questions=questions,
            seed=run_seed,  # Return the seed used for this request
            dungeon_id=dungeon_id,
            floor=floor
        )
        
        logger.info(f"Retrieved {len(questions)} questions for user {current_user.id}")
        return response
        
    except DungeonNotFoundError:
        logger.warning(f"Dungeon not found: {dungeon_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dungeon not found: {dungeon_id}"
        )
    except ContentError as e:
        logger.error(f"Content error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to fetch questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch questions"
        )


@router.get("/daily", response_model=DailyChallengeResponse)
async def get_daily_challenge(
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> DailyChallengeResponse:
    """
    Get current daily challenge.
    
    Returns today's daily challenge. Same for all users on the same day.
    Features:
    - Hard difficulty questions only
    - Random category (different each day)
    - 2x XP and 1.5x points bonus
    """
    content_service, session = service_session
    
    try:
        logger.info(f"Fetching daily challenge for user: {current_user.id}")
        challenge = await content_service.get_daily_challenge(session)
        logger.info(f"Retrieved daily challenge {challenge.id} for user: {current_user.id}")
        return challenge
        
    except DailyChallengeError as e:
        logger.error(f"Daily challenge error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate daily challenge"
        )
    except Exception as e:
        logger.error(f"Failed to fetch daily challenge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily challenge"
        )


@router.get("/daily/{challenge_id}/questions", response_model=QuestionsResponse)
async def get_daily_challenge_questions(
    challenge_id: UUID,
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> QuestionsResponse:
    """
    Get questions for daily challenge.
    
    Returns 10 hard difficulty questions for today's challenge.
    """
    content_service, session = service_session
    
    try:
        logger.info(f"Fetching questions for daily challenge {challenge_id}, user: {current_user.id}")
        
        questions = await content_service.get_daily_challenge_questions(
            challenge_id=challenge_id,
            user_id=current_user.id,
            session=session
        )
        
        # Get challenge for metadata
        challenge = await session.get(DailyChallenge, challenge_id)
        
        response = QuestionsResponse(
            questions=questions,
            seed=challenge.seed if challenge else 0,
            dungeon_id=challenge.dungeon_id if challenge else UUID('00000000-0000-0000-0000-000000000000'),
            floor=1  # Daily challenges are floor 1 equivalent
        )
        
        logger.info(f"Retrieved {len(questions)} hard questions for daily challenge")
        return response
        
    except DailyChallengeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily challenge not found"
        )
    except Exception as e:
        logger.error(f"Failed to fetch daily challenge questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily challenge questions"
        )


@router.post("/refresh-questions")
async def refresh_question_pool(
    category: Optional[str] = Query(None, description="Category to refresh (admin only)"),
    batch_size: int = Query(default=50, ge=10, le=100, description="Number of questions to fetch"),
    service_session: tuple[ContentService, AsyncSession] = Depends(get_content_service_with_session),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Refresh question pool from external APIs.
    
    Admin endpoint to refresh the question database with new content from external trivia APIs.
    """
    content_service, session = service_session
    
    # TODO: Add admin role check here
    # For now, allow any authenticated user for testing purposes
    
    try:
        from ....domain.enums import DungeonCategory
        
        # Convert string to enum if provided
        category_enum = None
        if category:
            try:
                category_enum = DungeonCategory(category.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}. Valid options: {[c.value for c in DungeonCategory]}"
                )
        
        logger.info(f"Refreshing question pool for category: {category_enum}, batch_size: {batch_size}")
        
        questions_added = await content_service.refresh_question_pool(
            category=category_enum,
            batch_size=batch_size,
            session=session
        )
        
        logger.info(f"Question pool refresh completed: {questions_added} questions added")
        
        return {
            "message": "Question pool refreshed successfully",
            "questions_added": questions_added,
            "category": category_enum.value if category_enum else "all",
            "batch_size": batch_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh question pool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh question pool"
        )
