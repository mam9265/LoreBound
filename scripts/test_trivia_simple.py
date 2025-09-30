#!/usr/bin/env python3
"""Simple test for trivia API client only."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Simple test just for the client
async def test_basic_trivia():
    """Test trivia API client with minimal dependencies."""
    print("Testing Trivia API Client...")
    
    # Import directly with reduced dependencies
    from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
    
    async with TriviaAPIClient() as client:
        try:
            # Test OpenTDB connection
            print("Testing OpenTDB API connection...")
            questions = await client.fetch_questions(amount=2, provider=TriviaAPIProvider.OPENTDB)
            
            if questions:
                print(f"SUCCESS: Fetched {len(questions)} questions from OpenTDB")
                q = questions[0]
                print(f"Sample: {q.question[:50]}...")
                print(f"Answer: {q.correct_answer}")
                print(f"Category: {q.category}")
            else:
                print("FAILED: No questions received")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_trivia())
