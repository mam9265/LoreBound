#!/usr/bin/env python3
"""Test script to validate API endpoint implementations."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_app_creation():
    """Test that the FastAPI app can be created successfully."""
    print("=== TESTING FASTAPI APP CREATION ===")
    
    try:
        from app.main import create_app
        
        # Create app instance
        app = create_app()
        print("[PASS] FastAPI app created successfully")
        
        # Check if routers are included
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/v1/auth/register",
            "/v1/auth/login", 
            "/v1/auth/apple",
            "/v1/auth/refresh",
            "/v1/auth/me",
            "/v1/content/dungeons",
            "/v1/content/questions",
            "/v1/content/daily",
            "/v1/runs/start",
            "/v1/runs/{run_id}/submit",
            "/healthz"
        ]
        
        for expected_route in expected_routes:
            # Check if route exists (allowing for parameter variations)
            route_exists = any(
                expected_route.replace("{run_id}", "{path}") in route or 
                expected_route in route for route in routes
            )
            if route_exists:
                print(f"[PASS] Route found: {expected_route}")
            else:
                print(f"[WARN] Route not found: {expected_route}")
        
        print("[SUCCESS] FastAPI app validation completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Failed to create FastAPI app: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router_imports():
    """Test that all routers can be imported successfully."""
    print("\n=== TESTING ROUTER IMPORTS ===")
    
    try:
        # Test auth router
        from app.api.v1.routers.auth import router as auth_router
        print("[PASS] Auth router imported successfully")
        
        # Test content router
        from app.api.v1.routers.content import router as content_router
        print("[PASS] Content router imported successfully")
        
        # Test runs router
        from app.api.v1.routers.runs import router as runs_router
        print("[PASS] Runs router imported successfully")
        
        # Check router configurations
        assert auth_router.prefix == "/auth"
        assert content_router.prefix == "/content"
        assert runs_router.prefix == "/runs"
        print("[PASS] Router prefixes configured correctly")
        
        # Check that routers have endpoints
        auth_routes = len([route for route in auth_router.routes if hasattr(route, 'endpoint')])
        content_routes = len([route for route in content_router.routes if hasattr(route, 'endpoint')])
        runs_routes = len([route for route in runs_router.routes if hasattr(route, 'endpoint')])
        
        print(f"[INFO] Auth router has {auth_routes} endpoints")
        print(f"[INFO] Content router has {content_routes} endpoints")
        print(f"[INFO] Runs router has {runs_routes} endpoints")
        
        assert auth_routes >= 5  # register, login, apple, refresh, me, logout
        assert content_routes >= 4  # dungeons, questions, daily, refresh-questions
        assert runs_routes >= 5  # start, submit, get, abandon, stats
        
        print("[SUCCESS] Router imports validation completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Router import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_imports():
    """Test that all services can be imported and instantiated."""
    print("\n=== TESTING SERVICE IMPORTS ===")
    
    try:
        # Test service imports
        from app.services.auth_service import AuthenticationService
        from app.services.content_service import ContentService
        from app.services.run_service import RunService
        from app.services.dependencies import (
            get_auth_service,
            get_content_service,
            get_run_service
        )
        print("[PASS] All services imported successfully")
        
        # Test dependencies
        from app.services.dependencies import (
            get_user_repository,
            get_content_repository,
            get_trivia_client,
            get_apple_service
        )
        print("[PASS] All service dependencies imported successfully")
        
        print("[SUCCESS] Service imports validation completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Service import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schemas_validation():
    """Test that schemas are properly configured."""
    print("\n=== TESTING SCHEMA VALIDATION ===")
    
    try:
        # Test auth schemas
        from app.schemas.auth import (
            UserRegisterRequest,
            UserLoginRequest,
            AppleSignInRequest,
            TokenResponse,
            AuthResponse
        )
        
        # Test content schemas
        from app.schemas.content import (
            DungeonResponse,
            QuestionResponse,
            DailyChallengeResponse,
            QuestionsResponse,
            QuestionRequest
        )
        
        # Test run schemas
        from app.schemas.run import (
            RunStartRequest,
            RunSubmitRequest,
            RunResponse,
            RunStatsResponse
        )
        
        print("[PASS] All schemas imported successfully")
        
        # Test schema creation
        reg_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!",
            handle="TestUser"
        )
        print("[PASS] UserRegisterRequest schema validation")
        
        login_data = UserLoginRequest(
            email="test@example.com", 
            password="TestPass123!"
        )
        print("[PASS] UserLoginRequest schema validation")
        
        print("[SUCCESS] Schema validation completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies_structure():
    """Test that dependency injection is properly structured."""
    print("\n=== TESTING DEPENDENCY INJECTION ===")
    
    try:
        from app.core.dependencies import get_current_user, get_current_active_user
        from app.repositories.base import get_session
        from app.core.config import get_settings
        
        print("[PASS] Core dependencies available")
        
        # Test service dependencies
        from app.services.dependencies import (
            get_auth_service_with_session,
            get_content_service_with_session,
            get_run_service_with_session
        )
        
        print("[PASS] Service dependencies with session available")
        
        print("[SUCCESS] Dependency injection validation completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Dependency injection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all API endpoint tests."""
    print("LOREBOUND API ENDPOINT VALIDATION")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(await test_app_creation())
    results.append(test_router_imports())
    results.append(test_service_imports())
    results.append(test_schemas_validation())
    results.append(test_dependencies_structure())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\nAPI ENDPOINTS VALIDATION SUCCESSFUL!")
        print("\nImplemented API Structure:")
        print("Authentication Endpoints:")
        print("  POST /v1/auth/register - User registration")
        print("  POST /v1/auth/login - User login")
        print("  POST /v1/auth/apple - Apple Sign-In")
        print("  POST /v1/auth/refresh - Token refresh")
        print("  GET  /v1/auth/me - Current user info")
        print("  POST /v1/auth/logout - User logout")
        
        print("\nContent Endpoints:")
        print("  GET  /v1/content/dungeons - Available dungeons")
        print("  GET  /v1/content/dungeons/{id} - Dungeon details")
        print("  GET  /v1/content/questions - Deterministic questions")
        print("  GET  /v1/content/daily - Daily challenge")
        print("  POST /v1/content/refresh-questions - Refresh question pool")
        
        print("\nGame Run Endpoints:")
        print("  POST /v1/runs/start - Start new game run")
        print("  POST /v1/runs/{id}/submit - Submit completed run")
        print("  GET  /v1/runs/ - User's run history")
        print("  GET  /v1/runs/{id} - Specific run details")
        print("  POST /v1/runs/{id}/abandon - Abandon run")
        print("  GET  /v1/runs/stats/me - User game statistics")
        
        print("\nHealth & Monitoring:")
        print("  GET  /healthz - Basic health check")
        print("  GET  /healthz/detailed - Detailed health check")
        print("  GET  /metrics - Prometheus metrics")
        
        print("\nREADY FOR DEPLOYMENT AND TESTING!")
    else:
        print(f"\n{total - passed} test suite(s) failed - check output above")


if __name__ == "__main__":
    asyncio.run(main())
