#!/usr/bin/env python3
"""Debug script to test registration step by step."""

import asyncio
import sys
import traceback
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.repositories.base import get_session
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthenticationService
from app.services.apple_service import AppleSignInService
from app.schemas.auth import UserRegisterRequest

async def debug_registration():
    """Debug the registration process step by step."""
    print("=== DEBUGGING REGISTRATION PROCESS ===")
    
    try:
        # Test configuration
        print(f"Environment: {settings.app_env}")
        print(f"Database URL: {settings.database_url[:50]}...")
        print(f"Debug mode: {settings.debug}")
        
        # Test database connection
        from app.repositories.base import test_database_connection
        db_connected = await test_database_connection()
        print(f"Database connected: {db_connected}")
        
        if not db_connected:
            print("[ERROR] Database connection failed - cannot proceed")
            return
        
        # Create services
        async for session in get_session():
            try:
                user_repo = UserRepository(session)
                apple_service = AppleSignInService(settings)
                auth_service = AuthenticationService(user_repo, apple_service, settings)
                
                # Test user registration
                print("\n=== Testing Registration ===")
                
                registration_data = UserRegisterRequest(
                    email="debug@example.com",
                    password="SecurePassword123!",
                    handle="DebugPlayer"
                )
                
                print(f"Registration data: {registration_data.model_dump()}")
                
                # Check if user already exists
                existing_user = await user_repo.get_user_by_email(registration_data.email.lower())
                if existing_user:
                    print(f"[INFO] User already exists: {existing_user.id}")
                    # Delete existing user for clean test
                    await session.execute(
                        f"DELETE FROM profiles WHERE user_id = '{existing_user.id}'"
                    )
                    await session.execute(
                        f"DELETE FROM users WHERE id = '{existing_user.id}'"
                    )
                    await session.commit()
                    print("[INFO] Deleted existing user for clean test")
                
                # Check if handle exists
                existing_handle = await user_repo.get_profile_by_handle(registration_data.handle)
                if existing_handle:
                    print(f"[ERROR] Handle already exists: {existing_handle.handle}")
                    return
                
                # Try registration
                print("[INFO] Attempting registration...")
                result = await auth_service.register_user(registration_data, session)
                print(f"[SUCCESS] Registration successful! User ID: {result.user.id}")
                print(f"   Access token length: {len(result.tokens.access_token)}")
                
                break
                
            except Exception as e:
                print(f"[ERROR] Registration failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                traceback.print_exc()
                await session.rollback()
                break
                
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_registration())
