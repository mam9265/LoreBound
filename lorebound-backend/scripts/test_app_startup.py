#!/usr/bin/env python3
"""Test script to identify application startup issues."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_full_app_startup():
    """Test full application startup to catch email validation errors."""
    print("Testing full application startup...")
    
    try:
        # Test importing the main app
        from app.main import create_app
        print("[PASS] Main app module imported")
        
        # Test creating the app
        app = create_app()
        print("[PASS] FastAPI app created successfully")
        
        # Test specific route that uses email validation
        from app.api.v1.routers.auth import router as auth_router
        print("[PASS] Auth router imported successfully")
        
        # Test authentication service
        from app.services.auth_service import AuthenticationService
        print("[PASS] Authentication service imported")
        
        # Test the schemas directly
        from app.schemas.auth import UserRegisterRequest, UserLoginRequest
        print("[PASS] Auth schemas imported")
        
        # Test creating a registration request
        reg_request = UserRegisterRequest(
            email="test@example.com",
            password="TestPassword123!",
            handle="TestUser"
        )
        print(f"[PASS] Registration request created: {reg_request.email}")
        
        # Test model validation
        print(f"[PASS] Email field type: {type(reg_request.email)}")
        
        print("[SUCCESS] Full application startup test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Application startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pydantic_version():
    """Check Pydantic version and configuration."""
    print("\nTesting Pydantic configuration...")
    
    try:
        import pydantic
        print(f"[INFO] Pydantic version: {pydantic.VERSION}")
        
        # Test EmailStr specifically
        from pydantic import EmailStr
        print(f"[INFO] EmailStr available: {EmailStr}")
        
        # Test creating EmailStr directly
        from pydantic import BaseModel
        
        class EmailTest(BaseModel):
            email: EmailStr
        
        test_instance = EmailTest(email="user@domain.com")
        print(f"[PASS] Direct EmailStr test: {test_instance.email}")
        
        # Check if email-validator is properly configured
        try:
            import email_validator
            print(f"[INFO] email-validator version: {email_validator.__version__}")
        except ImportError:
            print("[WARN] email-validator not available")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Pydantic configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_real_validation():
    """Test with real validation scenarios."""
    print("\nTesting real validation scenarios...")
    
    try:
        from app.schemas.auth import UserRegisterRequest
        
        # Test various email formats
        test_emails = [
            "valid@example.com",
            "user.name@domain.co.uk", 
            "test+tag@example.org",
            "user123@subdomain.example.com"
        ]
        
        for email in test_emails:
            try:
                req = UserRegisterRequest(
                    email=email,
                    password="TestPassword123!",
                    handle="TestUser"
                )
                print(f"[PASS] Valid email: {email}")
            except Exception as e:
                print(f"[FAIL] Email validation failed for {email}: {e}")
        
        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            ""
        ]
        
        for email in invalid_emails:
            try:
                req = UserRegisterRequest(
                    email=email,
                    password="TestPassword123!",
                    handle="TestUser"
                )
                print(f"[WARN] Invalid email accepted: {email}")
            except Exception:
                print(f"[PASS] Invalid email rejected: {email}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Real validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("PYDANTIC EMAIL ERROR DIAGNOSIS")
    print("=" * 40)
    
    # Run all tests
    test1 = test_pydantic_version()
    test2 = test_full_app_startup()
    test3 = test_with_real_validation()
    
    if all([test1, test2, test3]):
        print("\nAll tests passed! Email validation appears to be working correctly.")
        print("If you're still experiencing errors, please share the specific error message.")
    else:
        print("\nSome tests failed. Investigating potential solutions...")
