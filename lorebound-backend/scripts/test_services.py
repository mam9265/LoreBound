#!/usr/bin/env python3
"""Test script for validating service implementations."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
from app.services.apple_service import AppleSignInService
from app.core.config import settings
from app.domain.enums import QuestionDifficulty


async def test_trivia_api():
    """Test trivia API client."""
    print("🧪 Testing Trivia API Client...")
    
    async with TriviaAPIClient() as client:
        try:
            # Test connection
            print("Testing API connection...")
            is_connected = await client.test_connection(TriviaAPIProvider.OPENTDB)
            print(f"✅ OpenTDB connection: {'SUCCESS' if is_connected else 'FAILED'}")
            
            # Test fetching categories
            print("\nFetching categories...")
            categories = await client.get_categories(TriviaAPIProvider.OPENTDB)
            print(f"✅ Found {len(categories)} categories")
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
            print(f"✅ Fetched {len(questions)} questions")
            
            if questions:
                q = questions[0]
                print(f"   Sample question: {q.question[:60]}...")
                print(f"   Correct answer: {q.correct_answer}")
                print(f"   Category: {q.category}, Difficulty: {q.difficulty}")
            
        except Exception as e:
            print(f"❌ Trivia API test failed: {e}")


async def test_apple_service():
    """Test Apple Sign-In service."""
    print("\n🍎 Testing Apple Sign-In Service...")
    
    apple_service = AppleSignInService(settings)
    
    # Test in development mode (simplified verification)
    if settings.app_env == "dev":
        print("Running in development mode - testing basic functionality...")
        
        # Create a mock token for testing
        import jwt
        mock_token = jwt.encode(
            {
                "sub": "test_user_123",
                "email": "test@example.com",
                "aud": "com.lorebound.app",
                "iss": "https://appleid.apple.com"
            },
            "secret",
            algorithm="HS256"
        )
        
        try:
            user_info = await apple_service.verify_identity_token(mock_token)
            print(f"✅ Mock token verification successful")
            print(f"   User ID: {user_info.sub}")
            print(f"   Email: {user_info.email}")
        except Exception as e:
            print(f"❌ Apple service test failed: {e}")
    else:
        print("Production mode detected - skipping Apple Sign-In test")


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing Configuration...")
    
    try:
        # Test basic config
        print(f"✅ App environment: {settings.app_env}")
        print(f"✅ Database URL configured: {'Yes' if settings.database_url else 'No'}")
        print(f"✅ Redis URL configured: {'Yes' if settings.redis_url else 'No'}")
        print(f"✅ JWT algorithm: {settings.jwt_algorithm}")
        print(f"✅ Access token TTL: {settings.access_token_ttl_seconds}s")
        
        # Test validation
        validation_result = settings.validate_config()
        if validation_result["valid"]:
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration validation issues:")
            for error in validation_result["errors"]:
                print(f"   ❌ {error}")
            for warning in validation_result["warnings"]:
                print(f"   ⚠️  {warning}")
                
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


async def main():
    """Run all service tests."""
    print("🚀 LoreBound Service Tests")
    print("=" * 40)
    
    # Test configuration first
    test_configuration()
    
    # Test trivia API
    await test_trivia_api()
    
    # Test Apple service
    await test_apple_service()
    
    print("\n✅ Service tests completed!")
    print("\n📝 Next steps:")
    print("1. Set up environment variables for database and Redis")
    print("2. Run database migrations: alembic upgrade head")
    print("3. Test API endpoints with these services")
    print("4. Add unit tests for each service")


if __name__ == "__main__":
    asyncio.run(main())
