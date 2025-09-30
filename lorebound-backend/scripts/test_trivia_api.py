#!/usr/bin/env python3
"""Simple test for trivia API client without dependencies."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_trivia_api():
    """Test trivia API client independently."""
    print("Testing Trivia API Client...")
    
    # Import after adding to path
    from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
    from app.domain.enums import QuestionDifficulty
    
    async with TriviaAPIClient() as client:
        try:
            # Test connection
            print("Testing OpenTDB API connection...")
            is_connected = await client.test_connection(TriviaAPIProvider.OPENTDB)
            print(f"OpenTDB connection: {'SUCCESS' if is_connected else 'FAILED'}")
            
            if not is_connected:
                print("Cannot proceed without API connection")
                return
            
            # Test fetching categories
            print("\nFetching categories...")
            categories = await client.get_categories(TriviaAPIProvider.OPENTDB)
            print(f"Found {len(categories)} categories")
            for cat in categories[:5]:  # Show first 5
                print(f"   - {cat.name} (ID: {cat.id})")
            
            # Test fetching questions
            print("\nFetching sample questions...")
            questions = await client.fetch_questions(
                amount=5,
                category="Sports",
                difficulty=QuestionDifficulty.MEDIUM,
                provider=TriviaAPIProvider.OPENTDB
            )
            print(f"Fetched {len(questions)} questions")
            
            if questions:
                q = questions[0]
                print(f"\nSample question:")
                print(f"   Question: {q.question}")
                print(f"   Correct answer: {q.correct_answer}")
                print(f"   Wrong answers: {', '.join(q.incorrect_answers)}")
                print(f"   Category: {q.category}, Difficulty: {q.difficulty}")
                
            # Test different provider
            print("\nTesting alternative API...")
            try:
                alt_questions = await client.fetch_questions(
                    amount=3,
                    provider=TriviaAPIProvider.TRIVIA_API
                )
                print(f"Alternative API: Fetched {len(alt_questions)} questions")
            except Exception as e:
                print(f"Alternative API failed: {e}")
            
        except Exception as e:
            print(f"Trivia API test failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Run trivia API test."""
    print("LoreBound Trivia API Test")
    print("=" * 40)
    
    await test_trivia_api()
    
    print("\nTrivia API test completed!")
    print("\nNext steps:")
    print("1. Integrate with content service")
    print("2. Add question caching and storage")
    print("3. Implement deterministic selection")

if __name__ == "__main__":
    asyncio.run(main())
