"""Content service for managing dungeons, questions, and daily challenges."""

import logging
import random
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings
from ..domain.enums import DungeonCategory, QuestionDifficulty
from ..domain.models import Question, Dungeon, DungeonTier, DailyChallenge
from ..repositories.content_repo import ContentRepository
from ..schemas.content import (
    DungeonResponse,
    QuestionResponse,
    DailyChallengeResponse,
    QuestionRequest
)
from .trivia_api_client import TriviaAPIClient, TriviaAPIProvider, TriviaQuestion
from .exceptions import (
    ContentError,
    QuestionNotFoundError,
    DungeonNotFoundError,
    DailyChallengeError,
    TriviaAPIError
)

logger = logging.getLogger(__name__)


class ContentService:
    """Service for managing game content operations."""

    def __init__(
        self,
        content_repo: ContentRepository,
        trivia_client: TriviaAPIClient,
        settings: Settings
    ):
        self.content_repo = content_repo
        self.trivia_client = trivia_client
        self.settings = settings

    async def get_available_dungeons(self, session: AsyncSession) -> List[DungeonResponse]:
        """Get all available dungeons."""
        logger.info("Fetching available dungeons")

        try:
            dungeons = await self.content_repo.get_all_dungeons(session)
            return [DungeonResponse.model_validate(dungeon) for dungeon in dungeons]

        except Exception as e:
            logger.error(f"Failed to fetch dungeons: {e}")
            raise ContentError("Failed to fetch dungeons")

    async def get_dungeon_by_id(self, dungeon_id: UUID, session: AsyncSession) -> DungeonResponse:
        """Get specific dungeon by ID."""
        logger.info(f"Fetching dungeon: {dungeon_id}")

        dungeon = await self.content_repo.get_dungeon_by_id(dungeon_id, session)
        if not dungeon:
            raise DungeonNotFoundError(f"Dungeon not found: {dungeon_id}")

        return DungeonResponse.model_validate(dungeon)

    async def get_questions_for_dungeon(
        self,
        dungeon_id: UUID,
        floor: int,
        count: int,
        user_id: UUID,
        session: AsyncSession
    ) -> List[QuestionResponse]:
        """
        Get deterministic set of questions for a dungeon floor.
        Uses user ID and floor to generate consistent question selection.
        """
        logger.info(f"Getting {count} questions for dungeon {dungeon_id}, floor {floor}, user {user_id}")

        try:
            # Get dungeon to determine category and difficulty
            dungeon = await self.content_repo.get_dungeon_by_id(dungeon_id, session)
            if not dungeon:
                raise DungeonNotFoundError(f"Dungeon not found: {dungeon_id}")

            # Generate deterministic seed for question selection
            seed = self._generate_question_seed(user_id, dungeon_id, floor)
            
            # Get questions using deterministic selection
            questions = await self._get_deterministic_questions(
                category=dungeon.category,
                floor=floor,
                count=count,
                seed=seed,
                session=session
            )

            if len(questions) < count:
                # If we don't have enough questions in database, fetch from external API
                logger.info(f"Insufficient questions in database ({len(questions)}/{count}), fetching from external API")
                questions = await self._supplement_questions_from_api(
                    category=dungeon.category,
                    floor=floor,
                    count=count,
                    existing_questions=questions,
                    session=session
                )

            return [QuestionResponse.model_validate(q) for q in questions]

        except Exception as e:
            logger.error(f"Failed to get questions for dungeon: {e}")
            raise ContentError(f"Failed to get questions: {e}")

    async def get_daily_challenge(self, session: AsyncSession) -> DailyChallengeResponse:
        """Get current daily challenge."""
        logger.info("Fetching daily challenge")

        try:
            # Get current date for challenge lookup
            today = datetime.now(timezone.utc).date()
            
            # Check if we have a current daily challenge
            challenge = await self.content_repo.get_daily_challenge_by_date(today, session)
            
            if not challenge:
                # Generate new daily challenge
                logger.info(f"Generating new daily challenge for {today}")
                challenge = await self._generate_daily_challenge(today, session)

            return DailyChallengeResponse.model_validate(challenge)

        except Exception as e:
            logger.error(f"Failed to get daily challenge: {e}")
            raise DailyChallengeError(f"Failed to get daily challenge: {e}")

    async def refresh_question_pool(
        self,
        category: Optional[DungeonCategory] = None,
        batch_size: int = 50,
        session: AsyncSession = None
    ) -> int:
        """
        Refresh question pool from external trivia APIs.
        This can be run as a background job to keep questions fresh.
        """
        logger.info(f"Refreshing question pool for category: {category}")

        try:
            total_added = 0
            categories_to_fetch = [category] if category else list(DungeonCategory)

            async with self.trivia_client:
                for cat in categories_to_fetch:
                    for difficulty in QuestionDifficulty:
                        try:
                            # Fetch questions from external API
                            external_questions = await self.trivia_client.fetch_questions(
                                amount=batch_size,
                                category=cat.value,
                                difficulty=difficulty,
                                provider=TriviaAPIProvider.OPENTDB
                            )

                            # Convert and store questions
                            for ext_q in external_questions:
                                # Check if question already exists (prevent duplicates)
                                existing = await self.content_repo.get_question_by_hash(
                                    self._hash_question(ext_q.question), session
                                )
                                
                                if not existing:
                                    await self._store_external_question(ext_q, cat, difficulty, session)
                                    total_added += 1

                        except TriviaAPIError as e:
                            logger.warning(f"Failed to fetch questions for {cat.value}/{difficulty.value}: {e}")
                            continue

            logger.info(f"Successfully added {total_added} new questions to pool")
            return total_added

        except Exception as e:
            logger.error(f"Failed to refresh question pool: {e}")
            raise ContentError(f"Failed to refresh question pool: {e}")

    async def _get_deterministic_questions(
        self,
        category: DungeonCategory,
        floor: int,
        count: int,
        seed: str,
        session: AsyncSession
    ) -> List[Question]:
        """Get deterministic set of questions based on seed."""
        # Calculate difficulty based on floor
        difficulty = self._calculate_floor_difficulty(floor)
        
        # Get available questions for this category and difficulty
        available_questions = await self.content_repo.get_questions_by_category_and_difficulty(
            category, difficulty, session
        )

        if not available_questions:
            return []

        # Use seed to deterministically select questions
        random.seed(seed)
        selected_count = min(count, len(available_questions))
        selected_questions = random.sample(available_questions, selected_count)
        
        # Reset random seed to avoid affecting other operations
        random.seed()
        
        return selected_questions

    async def _supplement_questions_from_api(
        self,
        category: DungeonCategory,
        floor: int,
        count: int,
        existing_questions: List[Question],
        session: AsyncSession
    ) -> List[Question]:
        """Supplement existing questions with API-fetched questions."""
        needed_count = count - len(existing_questions)
        if needed_count <= 0:
            return existing_questions

        try:
            difficulty = self._calculate_floor_difficulty(floor)
            
            async with self.trivia_client:
                # Fetch questions from external API
                external_questions = await self.trivia_client.fetch_questions(
                    amount=needed_count * 2,  # Fetch extra in case some are duplicates
                    category=category.value,
                    difficulty=difficulty,
                    provider=TriviaAPIProvider.OPENTDB
                )

                # Convert external questions to our format and store them
                new_questions = []
                for ext_q in external_questions:
                    if len(new_questions) >= needed_count:
                        break

                    # Check if this question is already in existing set
                    question_hash = self._hash_question(ext_q.question)
                    if any(self._hash_question(q.question_text) == question_hash for q in existing_questions):
                        continue

                    # Store and add to result
                    stored_question = await self._store_external_question(ext_q, category, difficulty, session)
                    new_questions.append(stored_question)

                return existing_questions + new_questions[:needed_count]

        except Exception as e:
            logger.warning(f"Failed to supplement questions from API: {e}")
            return existing_questions  # Return what we have

    async def _store_external_question(
        self,
        external_question: TriviaQuestion,
        category: DungeonCategory,
        difficulty: QuestionDifficulty,
        session: AsyncSession
    ) -> Question:
        """Store external question in our database."""
        # Create all possible choices (correct + incorrect)
        all_choices = [external_question.correct_answer] + external_question.incorrect_answers
        random.shuffle(all_choices)  # Randomize choice order
        
        # Find correct answer index after shuffling
        correct_choice_index = all_choices.index(external_question.correct_answer)

        # Create question request schema
        question_data = QuestionRequest(
            question_text=external_question.question,
            choices=all_choices,
            correct_choice_index=correct_choice_index,
            category=category,
            difficulty=difficulty,
            source="external_api",
            metadata={
                "source_id": external_question.source_id,
                "original_category": external_question.category,
                "api_provider": "opentdb"
            }
        )

        # Store in database
        return await self.content_repo.create_question(question_data, session)

    async def _generate_daily_challenge(
        self,
        challenge_date: datetime.date,
        session: AsyncSession
    ) -> DailyChallenge:
        """Generate a new daily challenge."""
        # Use date as seed for deterministic challenge generation
        seed = f"daily_challenge_{challenge_date}_{self.settings.feature_flags_seed}"
        random.seed(seed)

        try:
            # Randomly select category and parameters for daily challenge
            category = random.choice(list(DungeonCategory))
            question_count = random.randint(5, 10)
            difficulty = random.choice(list(QuestionDifficulty))
            
            # Create daily challenge
            challenge_data = {
                "challenge_date": challenge_date,
                "category": category,
                "question_count": question_count,
                "difficulty": difficulty,
                "seed": seed,
                "metadata": {
                    "theme": f"Daily {category.value.title()} Challenge",
                    "description": f"Test your {category.value} knowledge with {question_count} {difficulty.value} questions!"
                }
            }

            challenge = await self.content_repo.create_daily_challenge(challenge_data, session)
            
            logger.info(f"Generated daily challenge: {challenge.id} for {challenge_date}")
            return challenge

        except Exception as e:
            logger.error(f"Failed to generate daily challenge: {e}")
            raise DailyChallengeError(f"Failed to generate daily challenge: {e}")
        finally:
            # Reset random seed
            random.seed()

    def _generate_question_seed(self, user_id: UUID, dungeon_id: UUID, floor: int) -> str:
        """Generate deterministic seed for question selection."""
        # Combine user ID, dungeon ID, floor, and global seed for consistency
        seed_string = f"{user_id}_{dungeon_id}_{floor}_{self.settings.feature_flags_seed}"
        return hashlib.sha256(seed_string.encode()).hexdigest()[:16]

    def _calculate_floor_difficulty(self, floor: int) -> QuestionDifficulty:
        """Calculate question difficulty based on dungeon floor."""
        if floor <= 3:
            return QuestionDifficulty.EASY
        elif floor <= 7:
            return QuestionDifficulty.MEDIUM
        else:
            return QuestionDifficulty.HARD

    def _hash_question(self, question_text: str) -> str:
        """Generate hash for question to detect duplicates."""
        return hashlib.md5(question_text.lower().strip().encode()).hexdigest()

    async def create_custom_dungeon(
        self,
        title: str,
        category: DungeonCategory,
        floor_count: int = 10,
        session: AsyncSession = None
    ) -> DungeonResponse:
        """Create a custom dungeon (admin function)."""
        logger.info(f"Creating custom dungeon: {title}")

        try:
            dungeon_data = {
                "title": title,
                "category": category,
                "content_version": 1,
                "metadata": {
                    "created_by": "content_service",
                    "custom": True
                }
            }

            dungeon = await self.content_repo.create_dungeon(dungeon_data, session)

            # Create dungeon tiers/floors
            for floor in range(1, floor_count + 1):
                tier_data = {
                    "dungeon_id": dungeon.id,
                    "floor": floor,
                    "boss_meta": {
                        "name": f"Floor {floor} Challenge",
                        "difficulty": self._calculate_floor_difficulty(floor).value,
                        "questions_count": 10
                    }
                }
                await self.content_repo.create_dungeon_tier(tier_data, session)

            logger.info(f"Successfully created custom dungeon: {dungeon.id}")
            return DungeonResponse.model_validate(dungeon)

        except Exception as e:
            logger.error(f"Failed to create custom dungeon: {e}")
            raise ContentError(f"Failed to create custom dungeon: {e}")


# Dependency for getting content service
def get_content_service(
    content_repo: ContentRepository,
    trivia_client: TriviaAPIClient,
    settings: Settings
) -> ContentService:
    """Dependency to get content service."""
    return ContentService(content_repo, trivia_client, settings)
