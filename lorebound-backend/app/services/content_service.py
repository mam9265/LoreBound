"""Content service for managing dungeons, questions, and daily challenges."""

import logging
import random
import hashlib
from datetime import datetime, timezone, timedelta, date
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
            dungeons = await self.content_repo.get_all_dungeons()
            return [DungeonResponse.model_validate(dungeon) for dungeon in dungeons]

        except Exception as e:
            logger.error(f"Failed to fetch dungeons: {e}")
            raise ContentError("Failed to fetch dungeons")

    async def get_dungeon_by_id(self, dungeon_id: UUID, session: AsyncSession) -> DungeonResponse:
        """Get specific dungeon by ID."""
        logger.info(f"Fetching dungeon: {dungeon_id}")

        dungeon = await self.content_repo.get_dungeon_by_id(dungeon_id)
        if not dungeon:
            raise DungeonNotFoundError(f"Dungeon not found: {dungeon_id}")

        return DungeonResponse.model_validate(dungeon)

    async def get_questions_for_dungeon(
        self,
        dungeon_id: UUID,
        floor: int,
        count: int,
        user_id: UUID,
        session: AsyncSession,
        run_seed: int = None
    ) -> List[QuestionResponse]:
        """
        Get questions for a dungeon floor.
        Uses run_seed to generate varied question selection per run.
        If run_seed is not provided, uses timestamp for random selection.
        """
        logger.info(f"Getting {count} questions for dungeon {dungeon_id}, floor {floor}, user {user_id}")

        try:
            # Get dungeon to determine category and difficulty
            dungeon = await self.content_repo.get_dungeon_by_id(dungeon_id)
            if not dungeon:
                raise DungeonNotFoundError(f"Dungeon not found: {dungeon_id}")

            # Use run_seed if provided, otherwise generate a unique seed per request
            if run_seed is None:
                # Use timestamp to ensure different questions each run
                import time
                run_seed = int(time.time() * 1000000) % (2**31)
            
            seed = self._generate_question_seed(user_id, dungeon_id, floor, run_seed)
            
            # Get questions using randomized selection
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
            challenge = await self.content_repo.get_daily_challenge_by_date(today)
            
            if not challenge:
                # Generate new daily challenge
                logger.info(f"Generating new daily challenge for {today}")
                challenge = await self._generate_daily_challenge(today, session)
                await session.commit()
                # Refresh to load relationships
                await session.refresh(challenge, ['dungeon'])

            # Ensure dungeon relationship is loaded
            if not hasattr(challenge, 'dungeon') or challenge.dungeon is None:
                from sqlalchemy.orm import selectinload
                stmt = select(DailyChallenge).where(DailyChallenge.id == challenge.id).options(selectinload(DailyChallenge.dungeon))
                result = await session.execute(stmt)
                challenge = result.scalar_one()

            return DailyChallengeResponse.model_validate(challenge)

        except Exception as e:
            logger.error(f"Failed to get daily challenge: {e}")
            raise DailyChallengeError(f"Failed to get daily challenge: {e}")
    
    async def get_daily_challenge_questions(
        self,
        challenge_id: UUID,
        user_id: UUID,
        session: AsyncSession
    ) -> List[QuestionResponse]:
        """Get hard difficulty questions for daily challenge."""
        logger.info(f"Getting questions for daily challenge {challenge_id}")
        
        try:
            # Get challenge details
            challenge = await session.get(DailyChallenge, challenge_id)
            if not challenge:
                raise DailyChallengeError(f"Daily challenge not found: {challenge_id}")
            
            # Get question count from modifiers first
            question_count = challenge.modifiers.get("question_count", 10)
            
            # Get dungeon
            dungeon = await self.content_repo.get_dungeon_by_id(challenge.dungeon_id)
            if not dungeon:
                raise DungeonNotFoundError(f"Dungeon not found: {challenge.dungeon_id}")
            
            # Get ONLY hard difficulty questions for this category
            from sqlalchemy import select
            from ..domain.models import Question, Dungeon
            
            hard_questions_result = await session.execute(
                select(Question).where(
                    Question.dungeon_id == dungeon.id,
                    Question.difficulty == QuestionDifficulty.HARD
                )
            )
            hard_questions = list(hard_questions_result.scalars().all())
            
            if len(hard_questions) < question_count:
                logger.warning(f"Insufficient hard questions ({len(hard_questions)}/{question_count}) for dungeon {dungeon.id}, fetching from API")
                # Try to fetch more hard questions from API
                hard_questions = await self._supplement_questions_from_api(
                    category=dungeon.category,
                    floor=10,  # Floor 10 = hard difficulty
                    count=question_count,
                    existing_questions=hard_questions,
                    session=session
                )
                await session.commit()  # Commit newly fetched questions
            
            # Use challenge seed for consistent question selection per day
            rng = random.Random(challenge.seed)
            rng.shuffle(hard_questions)
            
            # Select questions
            selected_questions = hard_questions[:min(question_count, len(hard_questions))]
            
            logger.info(f"Selected {len(selected_questions)} hard questions for daily challenge")
            return [QuestionResponse.model_validate(q) for q in selected_questions]
            
        except Exception as e:
            logger.error(f"Failed to get daily challenge questions: {e}")
            raise ContentError(f"Failed to get daily challenge questions: {e}")

    async def refresh_question_pool(
        self,
        category: Optional[str] = None,
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
            
            # Convert string category to enum if provided
            if category:
                # Validate category string
                valid_categories = [cat.value for cat in DungeonCategory]
                if category not in valid_categories:
                    raise ContentError(f"Invalid category: {category}. Valid options: {valid_categories}")
                categories_to_fetch = [DungeonCategory(category)]
            else:
                categories_to_fetch = list(DungeonCategory)

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
                                question_hash = self._hash_question(ext_q.question)
                                existing = await self.content_repo.get_question_by_hash(question_hash, session)
                                
                                if not existing:
                                    await self._store_external_question(ext_q, cat, difficulty, session)
                                    total_added += 1

                        except TriviaAPIError as e:
                            logger.warning(f"Failed to fetch questions for {cat.value}/{difficulty.value}: {e}")
                            continue

            # Commit all the new questions to database
            if session:
                await session.commit()
            
            logger.info(f"Successfully added {total_added} new questions to pool")
            return total_added

        except Exception as e:
            logger.error(f"Failed to refresh question pool: {e}")
            if session:
                await session.rollback()
            raise ContentError(f"Failed to refresh question pool: {e}")

    async def _get_deterministic_questions(
        self,
        category: DungeonCategory,
        floor: int,
        count: int,
        seed: str,
        session: AsyncSession
    ) -> List[Question]:
        """Get varied set of questions using seed for randomization."""
        # Get ALL questions for this category (not filtered by difficulty)
        # This ensures we have a large pool to select from
        from sqlalchemy import select
        from ..domain.models import Dungeon
        
        # Get dungeons for this category
        dungeons_result = await session.execute(
            select(Dungeon).where(Dungeon.category == category)
        )
        dungeons = list(dungeons_result.scalars().all())
        
        if not dungeons:
            return []
        
        # Get ALL questions for these dungeons (mix of all difficulties)
        available_questions = []
        for dungeon in dungeons:
            dungeon_questions = await self.content_repo.get_questions_for_dungeon(dungeon.id)
            available_questions.extend(dungeon_questions)

        if not available_questions:
            return []

        # Convert string seed to integer for proper randomization
        seed_int = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**31)
        
        # Create a local Random instance to avoid affecting global state
        rng = random.Random(seed_int)
        
        # Shuffle the entire pool to get different subsets each time
        rng.shuffle(available_questions)
        
        # Select the requested count from the shuffled pool
        selected_count = min(count, len(available_questions))
        selected_questions = available_questions[:selected_count]
        
        logger.info(f"Selected {len(selected_questions)} questions from pool of {len(available_questions)} (category: {category}, seed: {seed_int})")
        
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
                # Ensure category is a string
                if isinstance(category, DungeonCategory):
                    category_str = category.value
                elif isinstance(category, str):
                    category_str = category
                else:
                    category_str = str(category)
                    
                external_questions = await self.trivia_client.fetch_questions(
                    amount=needed_count * 2,  # Fetch extra in case some are duplicates
                    category=category_str,
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
                    if any(self._hash_question(q.prompt) == question_hash for q in existing_questions):
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

        # Get dungeon for this category
        dungeons = await self.content_repo.get_dungeons_by_category(category)
        if not dungeons:
            raise ContentError(f"No dungeons found for category: {category}")
        
        # Use first dungeon of this category
        dungeon = dungeons[0]
        
        # Store in database
        return await self.content_repo.create_question(
            dungeon_id=dungeon.id,
            prompt=external_question.question,
            choices=all_choices,
            answer_index=correct_choice_index,
            difficulty=difficulty,
            tags=[category.value, difficulty.value, "external_api"]
        )

    async def _generate_daily_challenge(
        self,
        challenge_date: date,
        session: AsyncSession
    ) -> DailyChallenge:
        """Generate a new daily challenge with hard questions and random category."""
        # Use date as seed for deterministic challenge generation
        seed_string = f"daily_challenge_{challenge_date}"
        seed_int = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**31)
        
        # Create local random instance
        rng = random.Random(seed_int)

        try:
            # Randomly select category (different each day based on date seed)
            category = rng.choice(list(DungeonCategory))
            
            # Daily challenges are always:
            # - Hard difficulty only
            # - 10 questions
            # - Bonus XP multiplier
            question_count = 10
            difficulty = QuestionDifficulty.HARD
            
            # Get dungeon for this category
            dungeons = await self.content_repo.get_dungeons_by_category(category)
            if not dungeons:
                raise DailyChallengeError(f"No dungeons found for category: {category}")
            
            dungeon = dungeons[0]
            
            # Calculate expiration (end of day UTC)
            from datetime import datetime as dt, time as dt_time
            expires_at = dt.combine(
                challenge_date + timedelta(days=1),
                dt_time.min
            ).replace(tzinfo=timezone.utc)
            
            # Create daily challenge with bonus modifier
            challenge = await self.content_repo.create_daily_challenge(
                challenge_date=challenge_date,
                seed=seed_int,
                dungeon_id=dungeon.id,
                modifiers={
                    "difficulty": difficulty.value,
                    "question_count": question_count,
                    "xp_multiplier": 2.0,  # 2x XP for daily challenges
                    "points_multiplier": 1.5,  # 1.5x points
                    "theme": f"Daily {category.value.title()} Challenge",
                    "description": f"Hard mode challenge! {question_count} difficult {category.value} questions with bonus rewards!"
                },
                expires_at=expires_at
            )
            
            logger.info(f"Generated daily challenge: {challenge.id} for {challenge_date} - Category: {category}, Difficulty: {difficulty}")
            return challenge

        except Exception as e:
            logger.error(f"Failed to generate daily challenge: {e}")
            raise DailyChallengeError(f"Failed to generate daily challenge: {e}")

    def _generate_question_seed(self, user_id: UUID, dungeon_id: UUID, floor: int, run_seed: int) -> str:
        """Generate seed for question selection based on run."""
        # Combine run seed with other factors for varied but reproducible selection
        seed_string = f"{run_seed}_{dungeon_id}_{floor}_{user_id}"
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
