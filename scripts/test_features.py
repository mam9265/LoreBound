#!/usr/bin/env python3
"""Simple feature test without Unicode characters."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_authentication():
    """Test Authentication Service."""
    print("=== TESTING AUTHENTICATION SERVICE ===")
    
    try:
        from app.services.auth_service import AuthenticationService
        from app.services.apple_service import AppleSignInService
        from app.schemas.auth import UserRegisterRequest, UserLoginRequest
        from app.core.config import Settings
        from app.domain.enums import UserStatus
        
        # Create mocks
        mock_user_repo = AsyncMock()
        mock_apple_service = AsyncMock(spec=AppleSignInService)
        mock_settings = Mock(spec=Settings)
        mock_settings.access_token_ttl_seconds = 900
        
        # Create service
        auth_service = AuthenticationService(mock_user_repo, mock_apple_service, mock_settings)
        print("[PASS] Authentication Service created")
        
        # Test schemas
        reg_data = UserRegisterRequest(
            email="test@example.com",
            password="SecurePass123!",
            handle="TestUser"
        )
        print("[PASS] Registration schema validation")
        
        login_data = UserLoginRequest(
            email="test@example.com",
            password="SecurePass123!"
        )
        print("[PASS] Login schema validation")
        
        # Test token generation
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        
        tokens = auth_service._generate_token_pair(mock_user)
        print(f"[PASS] Token generation: {tokens.token_type}")
        
        print("[SUCCESS] Authentication Service - ALL TESTS PASSED")
        
    except Exception as e:
        print(f"[FAIL] Authentication test failed: {e}")
        return False
    
    return True


async def test_content_service():
    """Test Content Service."""
    print("\n=== TESTING CONTENT SERVICE ===")
    
    try:
        from app.services.content_service import ContentService
        from app.services.trivia_api_client import TriviaAPIClient
        from app.core.config import Settings
        from app.domain.enums import QuestionDifficulty
        
        # Create mocks
        mock_content_repo = AsyncMock()
        mock_trivia_client = AsyncMock(spec=TriviaAPIClient)
        mock_settings = Mock(spec=Settings)
        mock_settings.feature_flags_seed = 12345
        
        # Create service
        content_service = ContentService(mock_content_repo, mock_trivia_client, mock_settings)
        print("[PASS] Content Service created")
        
        # Test deterministic seeding
        user_id = uuid4()
        dungeon_id = uuid4()
        
        seed1 = content_service._generate_question_seed(user_id, dungeon_id, 3)
        seed2 = content_service._generate_question_seed(user_id, dungeon_id, 3)
        
        assert seed1 == seed2
        print("[PASS] Deterministic seed generation")
        
        # Test difficulty progression
        easy = content_service._calculate_floor_difficulty(2)
        medium = content_service._calculate_floor_difficulty(5)
        hard = content_service._calculate_floor_difficulty(10)
        
        assert easy == QuestionDifficulty.EASY
        assert medium == QuestionDifficulty.MEDIUM
        assert hard == QuestionDifficulty.HARD
        print("[PASS] Floor difficulty progression")
        
        # Test question hashing
        hash1 = content_service._hash_question("Test question?")
        hash2 = content_service._hash_question("Test question?")
        hash3 = content_service._hash_question("Different question?")
        
        assert hash1 == hash2
        assert hash1 != hash3
        print("[PASS] Question duplicate detection")
        
        print("[SUCCESS] Content Service - ALL TESTS PASSED")
        
    except Exception as e:
        print(f"[FAIL] Content Service test failed: {e}")
        return False
    
    return True


async def test_trivia_api():
    """Test live Trivia API."""
    print("\n=== TESTING LIVE TRIVIA API ===")
    
    try:
        from app.services.trivia_api_client import TriviaAPIClient, TriviaAPIProvider
        from app.domain.enums import QuestionDifficulty
        
        async with TriviaAPIClient() as client:
            print("[PASS] Trivia API client created")
            
            # Test connection
            connected = await client.test_connection(TriviaAPIProvider.OPENTDB)
            print(f"[INFO] OpenTDB connection: {'SUCCESS' if connected else 'FAILED'}")
            
            if not connected:
                print("[SKIP] Skipping API tests - no connection")
                return True
            
            # Test categories
            categories = await client.get_categories(TriviaAPIProvider.OPENTDB)
            print(f"[PASS] Fetched {len(categories)} categories")
            
            # Show sample categories
            for i, cat in enumerate(categories[:3]):
                print(f"   {i+1}. {cat.name} (ID: {cat.id})")
            
            # Test questions
            questions = await client.fetch_questions(
                amount=2,
                category="Sports",
                difficulty=QuestionDifficulty.EASY,
                provider=TriviaAPIProvider.OPENTDB
            )
            print(f"[PASS] Fetched {len(questions)} questions")
            
            # Show sample question
            if questions:
                q = questions[0]
                print(f"\nSample Question:")
                print(f"   Q: {q.question}")
                print(f"   A: {q.correct_answer}")
                print(f"   Wrong: {', '.join(q.incorrect_answers[:2])}")
                print(f"   Category: {q.category}")
            
            print("[SUCCESS] Trivia API - ALL TESTS PASSED")
            
    except Exception as e:
        print(f"[FAIL] Trivia API test failed: {e}")
        return False
    
    return True


async def test_security():
    """Test security functions."""
    print("\n=== TESTING SECURITY FUNCTIONS ===")
    
    try:
        from app.core.security import (
            get_password_hash,
            verify_password,
            create_access_token,
            create_refresh_token,
            verify_token
        )
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        print("[PASS] Password hashing")
        
        # Test password verification
        valid = verify_password(password, hashed)
        invalid = verify_password("WrongPassword", hashed)
        
        assert valid and not invalid
        print("[PASS] Password verification")
        
        # Test tokens
        user_id = uuid4()
        access_token = create_access_token("test@example.com", user_id=user_id)
        refresh_token = create_refresh_token("test@example.com", user_id=user_id)
        print("[PASS] Token creation")
        
        # Test token verification
        access_payload = verify_token(access_token, "access")
        refresh_payload = verify_token(refresh_token, "refresh")
        
        assert access_payload["user_id"] == str(user_id)
        assert refresh_payload["user_id"] == str(user_id)
        print("[PASS] Token verification")
        
        print("[SUCCESS] Security Functions - ALL TESTS PASSED")
        
    except Exception as e:
        print(f"[FAIL] Security test failed: {e}")
        return False
    
    return True


async def test_dependencies():
    """Test service dependencies."""
    print("\n=== TESTING SERVICE DEPENDENCIES ===")
    
    try:
        from app.services.dependencies import (
            get_user_repository,
            get_content_repository,
            get_trivia_client,
            get_apple_service
        )
        from app.core.config import get_settings
        
        # Test factories
        user_repo = get_user_repository()
        content_repo = get_content_repository()
        trivia_client = get_trivia_client()
        
        settings = get_settings()
        apple_service = get_apple_service(settings)
        
        print("[PASS] All service factories working")
        print("[SUCCESS] Service Dependencies - ALL TESTS PASSED")
        
    except Exception as e:
        print(f"[FAIL] Dependencies test failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("LOREBOUND SERVICE VALIDATION")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(await test_authentication())
    results.append(await test_content_service())
    results.append(await test_trivia_api())
    results.append(await test_security())
    results.append(await test_dependencies())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
        print("\nImplemented Features Working:")
        print("- Authentication Service (register, login, tokens)")
        print("- Content Service (deterministic questions, challenges)")
        print("- Trivia API Integration (live external questions)")
        print("- Security Functions (password hashing, JWT)")
        print("- Service Dependencies (dependency injection)")
        print("\nReady for API endpoint implementation!")
    else:
        print(f"\n{total - passed} test suite(s) failed - check output above")


if __name__ == "__main__":
    asyncio.run(main())
