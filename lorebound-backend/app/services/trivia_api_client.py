"""Client for fetching trivia questions from external APIs."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
import aiohttp
from pydantic import BaseModel, Field
import random

from ..domain.enums import QuestionDifficulty
from .exceptions import TriviaAPIError

logger = logging.getLogger(__name__)


class TriviaAPIProvider(str, Enum):
    """Supported trivia API providers."""
    OPENTDB = "opentdb"
    TRIVIA_API = "trivia_api"


class TriviaCategory(BaseModel):
    """Trivia category information."""
    id: int
    name: str
    question_count: Optional[int] = None


class TriviaQuestion(BaseModel):
    """External trivia question data."""
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    category: str
    difficulty: str
    question_type: str = "multiple"  # multiple or boolean
    source_id: Optional[str] = None  # External API question ID


class TriviaAPIResponse(BaseModel):
    """Response from trivia API."""
    questions: List[TriviaQuestion]
    response_code: int = 0
    total_questions: Optional[int] = None


class TriviaAPIClient:
    """Client for fetching trivia questions from external APIs."""

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

        # OpenTDB configuration
        self.opentdb_base_url = "https://opentdb.com/api.php"
        self.opentdb_categories_url = "https://opentdb.com/api_category.php"
        
        # Trivia API configuration  
        self.trivia_api_base_url = "https://the-trivia-api.com/api/questions"

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_categories(self, provider: TriviaAPIProvider = TriviaAPIProvider.OPENTDB) -> List[TriviaCategory]:
        """Fetch available categories from trivia API."""
        if provider == TriviaAPIProvider.OPENTDB:
            return await self._get_opentdb_categories()
        elif provider == TriviaAPIProvider.TRIVIA_API:
            return await self._get_trivia_api_categories()
        else:
            raise TriviaAPIError(f"Unsupported provider: {provider}")

    async def fetch_questions(
        self,
        amount: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        provider: TriviaAPIProvider = TriviaAPIProvider.OPENTDB
    ) -> List[TriviaQuestion]:
        """
        Fetch trivia questions from external API.
        
        Args:
            amount: Number of questions to fetch (max 50 for OpenTDB)
            category: Category name or ID
            difficulty: Question difficulty level
            provider: Which API provider to use
            
        Returns:
            List of trivia questions
        """
        logger.info(f"Fetching {amount} questions from {provider.value}")

        if provider == TriviaAPIProvider.OPENTDB:
            return await self._fetch_opentdb_questions(amount, category, difficulty)
        elif provider == TriviaAPIProvider.TRIVIA_API:
            return await self._fetch_trivia_api_questions(amount, category, difficulty)
        else:
            raise TriviaAPIError(f"Unsupported provider: {provider}")

    async def _fetch_opentdb_questions(
        self,
        amount: int,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None
    ) -> List[TriviaQuestion]:
        """Fetch questions from Open Trivia Database."""
        if not self.session:
            raise TriviaAPIError("HTTP session not initialized")

        # Build parameters
        params = {
            "amount": min(amount, 50),  # OpenTDB max is 50
            "type": "multiple"  # Only multiple choice for now
        }

        if category:
            # Map category name to OpenTDB category ID
            category_id = await self._get_opentdb_category_id(category)
            if category_id:
                params["category"] = category_id

        if difficulty:
            # Map our difficulty enum to OpenTDB format
            difficulty_map = {
                QuestionDifficulty.EASY: "easy",
                QuestionDifficulty.MEDIUM: "medium", 
                QuestionDifficulty.HARD: "hard"
            }
            params["difficulty"] = difficulty_map.get(difficulty, "medium")

        # Fetch questions with retry logic
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(self.opentdb_base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_opentdb_response(data)
                    else:
                        logger.warning(f"OpenTDB returned status {response.status}")
                        if attempt == self.max_retries - 1:
                            raise TriviaAPIError(f"OpenTDB API error: {response.status}")

            except asyncio.TimeoutError:
                logger.warning(f"OpenTDB request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise TriviaAPIError("OpenTDB request timeout")

            except Exception as e:
                logger.error(f"OpenTDB request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise TriviaAPIError(f"OpenTDB request failed: {e}")

            # Wait before retry
            await asyncio.sleep(2 ** attempt)

        raise TriviaAPIError("Max retries exceeded")

    async def _fetch_trivia_api_questions(
        self,
        amount: int,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None
    ) -> List[TriviaQuestion]:
        """Fetch questions from The Trivia API."""
        if not self.session:
            raise TriviaAPIError("HTTP session not initialized")

        # Build parameters
        params = {"limit": min(amount, 20)}  # Trivia API max is 20

        if category:
            params["categories"] = category.lower()

        if difficulty:
            difficulty_map = {
                QuestionDifficulty.EASY: "easy",
                QuestionDifficulty.MEDIUM: "medium",
                QuestionDifficulty.HARD: "hard"
            }
            params["difficulty"] = difficulty_map.get(difficulty, "medium")

        # Fetch questions with retry logic
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(self.trivia_api_base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_trivia_api_response(data)
                    else:
                        logger.warning(f"Trivia API returned status {response.status}")
                        if attempt == self.max_retries - 1:
                            raise TriviaAPIError(f"Trivia API error: {response.status}")

            except asyncio.TimeoutError:
                logger.warning(f"Trivia API request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise TriviaAPIError("Trivia API request timeout")

            except Exception as e:
                logger.error(f"Trivia API request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise TriviaAPIError(f"Trivia API request failed: {e}")

            # Wait before retry
            await asyncio.sleep(2 ** attempt)

        raise TriviaAPIError("Max retries exceeded")

    async def _get_opentdb_categories(self) -> List[TriviaCategory]:
        """Fetch categories from OpenTDB."""
        if not self.session:
            raise TriviaAPIError("HTTP session not initialized")

        try:
            async with self.session.get(self.opentdb_categories_url) as response:
                if response.status == 200:
                    data = await response.json()
                    categories = []
                    for cat in data.get("trivia_categories", []):
                        categories.append(TriviaCategory(
                            id=cat["id"],
                            name=cat["name"]
                        ))
                    return categories
                else:
                    raise TriviaAPIError(f"Failed to fetch categories: {response.status}")

        except Exception as e:
            logger.error(f"Failed to fetch OpenTDB categories: {e}")
            raise TriviaAPIError(f"Failed to fetch categories: {e}")

    async def _get_trivia_api_categories(self) -> List[TriviaCategory]:
        """Get categories for The Trivia API (predefined list)."""
        # The Trivia API uses predefined categories
        categories = [
            "arts_and_literature", "film_and_tv", "food_and_drink", "general_knowledge",
            "geography", "history", "music", "science", "society_and_culture", "sport_and_leisure"
        ]
        
        return [
            TriviaCategory(id=i, name=cat.replace("_", " ").title())
            for i, cat in enumerate(categories)
        ]

    async def _get_opentdb_category_id(self, category_name: str) -> Optional[int]:
        """Get OpenTDB category ID by name."""
        categories = await self._get_opentdb_categories()
        for cat in categories:
            if cat.name.lower() == category_name.lower():
                return cat.id
        return None

    def _parse_opentdb_response(self, data: Dict[str, Any]) -> List[TriviaQuestion]:
        """Parse OpenTDB API response."""
        response_code = data.get("response_code", 1)
        
        if response_code != 0:
            error_messages = {
                1: "No results - insufficient questions in database",
                2: "Invalid parameter - contains invalid parameter",
                3: "Token not found - session token not found",
                4: "Token empty - session token empty"
            }
            raise TriviaAPIError(f"OpenTDB error: {error_messages.get(response_code, 'Unknown error')}")

        questions = []
        for q in data.get("results", []):
            # Decode HTML entities if needed
            question_text = self._decode_html_entities(q.get("question", ""))
            correct_answer = self._decode_html_entities(q.get("correct_answer", ""))
            incorrect_answers = [
                self._decode_html_entities(ans) for ans in q.get("incorrect_answers", [])
            ]

            questions.append(TriviaQuestion(
                question=question_text,
                correct_answer=correct_answer,
                incorrect_answers=incorrect_answers,
                category=q.get("category", "General"),
                difficulty=q.get("difficulty", "medium"),
                question_type=q.get("type", "multiple"),
                source_id=f"opentdb_{hash(question_text)}"
            ))

        return questions

    def _parse_trivia_api_response(self, data: List[Dict[str, Any]]) -> List[TriviaQuestion]:
        """Parse The Trivia API response."""
        questions = []
        
        for q in data:
            # The Trivia API returns data in a different format
            question_text = q.get("question", "")
            correct_answer = q.get("correctAnswer", "")
            incorrect_answers = q.get("incorrectAnswers", [])

            questions.append(TriviaQuestion(
                question=question_text,
                correct_answer=correct_answer,
                incorrect_answers=incorrect_answers,
                category=q.get("category", "General"),
                difficulty=q.get("difficulty", "medium"),
                question_type="multiple",
                source_id=f"trivia_api_{q.get('id', hash(question_text))}"
            ))

        return questions

    def _decode_html_entities(self, text: str) -> str:
        """Decode HTML entities in text."""
        import html
        return html.unescape(text)

    async def test_connection(self, provider: TriviaAPIProvider = TriviaAPIProvider.OPENTDB) -> bool:
        """Test connection to trivia API."""
        try:
            questions = await self.fetch_questions(amount=1, provider=provider)
            return len(questions) > 0
        except Exception as e:
            logger.error(f"Trivia API connection test failed: {e}")
            return False


# Factory function for creating trivia client
def create_trivia_client() -> TriviaAPIClient:
    """Create and configure trivia API client."""
    return TriviaAPIClient(timeout=10, max_retries=3)
