#!/usr/bin/env python3
"""
Quick test script to verify dungeon category fix.
Run this to check if categories are properly mapped.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "lorebound-backend"))

async def test_category_mapping():
    """Test that all categories are properly mapped."""
    from app.services.trivia_api_client import TriviaAPIClient
    from app.domain.enums import DungeonCategory
    
    print("="*60)
    print("Testing Dungeon Category Mapping")
    print("="*60)
    
    client = TriviaAPIClient()
    
    async with client:
        print("\nFetching OpenTDB categories...")
        categories = await client._get_opentdb_categories()
        
        print(f"\n✓ Found {len(categories)} OpenTDB categories\n")
        
        # Test each dungeon category
        test_categories = [
            ("sports", "Sports"),
            ("music", "Entertainment: Music"),
            ("history", "History"),
            ("pop_culture", "Entertainment: Television"),
            ("books", "Entertainment: Books"),
            ("science", "Science & Nature"),
            ("geography", "Geography"),
            ("general", "General Knowledge"),
        ]
        
        print("Testing category mappings:\n")
        all_passed = True
        
        for game_category, expected_opentdb in test_categories:
            category_id = await client._get_opentdb_category_id(game_category)
            
            if category_id:
                # Find the actual category name
                actual_name = next((c.name for c in categories if c.id == category_id), "Unknown")
                status = "✓" if expected_opentdb in actual_name else "⚠"
                print(f"  {status} {game_category:15} → {actual_name} (ID: {category_id})")
            else:
                print(f"  ✗ {game_category:15} → FAILED TO MAP")
                all_passed = False
        
        print("\n" + "="*60)
        if all_passed:
            print("✅ ALL CATEGORY MAPPINGS WORKING!")
        else:
            print("❌ SOME MAPPINGS FAILED - Check logs above")
        print("="*60)


async def test_dungeon_questions():
    """Test that dungeons have questions or can fetch them."""
    from app.repositories.base import get_session
    from app.repositories.content_repo import ContentRepository
    from app.domain.models import Dungeon, Question
    from sqlalchemy import select, func
    
    print("\n" + "="*60)
    print("Testing Dungeon Questions")
    print("="*60)
    
    async for session in get_session():
        try:
            content_repo = ContentRepository(session)
            
            # Get all dungeons
            dungeons = await content_repo.get_all_dungeons()
            
            if not dungeons:
                print("\n⚠ No dungeons found in database!")
                print("Run: python lorebound-backend/scripts/seed_content_data.py")
                return
            
            print(f"\nFound {len(dungeons)} dungeons:\n")
            
            for dungeon in dungeons:
                # Count questions for this dungeon
                result = await session.execute(
                    select(func.count(Question.id))
                    .where(Question.dungeon_id == dungeon.id)
                )
                count = result.scalar() or 0
                
                icon = "✓" if count > 0 else "⚠"
                print(f"  {icon} {dungeon.title:30} ({dungeon.category:15}): {count:4} questions")
            
            # Overall stats
            total_result = await session.execute(select(func.count(Question.id)))
            total = total_result.scalar() or 0
            
            print("\n" + "="*60)
            print(f"Total Questions: {total}")
            
            if total < 100:
                print("\n💡 Tip: Run populate_questions.py to add more questions:")
                print("   cd lorebound-backend")
                print("   python scripts/populate_questions.py --count 50")
            else:
                print("✅ Good amount of questions available!")
            print("="*60)
            
        finally:
            await session.close()
            break


async def main():
    """Run all tests."""
    print("\n🔍 LoreBound Category Fix Verification\n")
    
    try:
        # Test 1: Category mapping
        await test_category_mapping()
        
        # Test 2: Dungeon questions
        await test_dungeon_questions()
        
        print("\n" + "="*60)
        print("✅ Verification Complete!")
        print("="*60)
        print("\nNext Steps:")
        print("1. If mappings work but questions are low, run:")
        print("   python lorebound-backend/scripts/populate_questions.py")
        print("\n2. Start your backend:")
        print("   cd lorebound-backend && uvicorn app.main:app --reload")
        print("\n3. Start your frontend and test!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nMake sure you're in the LoreBound root directory")
        print("and the backend is properly set up.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

