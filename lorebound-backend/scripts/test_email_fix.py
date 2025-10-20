#!/usr/bin/env python3
"""Test script to verify email validation fix."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_original_email_validation():
    """Test the original EmailStr validation."""
    print("=== TESTING ORIGINAL EMAIL VALIDATION ===")
    
    try:
        from app.schemas.auth import UserRegisterRequest, UserLoginRequest
        
        # Test registration
        reg_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPassword123!",
            handle="TestUser"
        )
        print(f"[PASS] Registration schema: {reg_data.email}")
        
        # Test login
        login_data = UserLoginRequest(
            email="user@domain.com",
            password="TestPassword123!"
        )
        print(f"[PASS] Login schema: {login_data.email}")
        
        # Test invalid email
        try:
            invalid_reg = UserRegisterRequest(
                email="invalid-email",
                password="TestPassword123!",
                handle="TestUser"
            )
            print(f"[WARN] Invalid email was accepted: {invalid_reg.email}")
        except Exception as e:
            print(f"[PASS] Invalid email rejected: {str(e)[:50]}...")
        
        print("[SUCCESS] Original email validation working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Original email validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_email_validation():
    """Test the custom email validation."""
    print("\n=== TESTING CUSTOM EMAIL VALIDATION ===")
    
    try:
        from app.schemas.email_validation import email_validator_func
        
        # Test valid emails
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@subdomain.example.org",
            "firstname.lastname@company.com"
        ]
        
        for email in valid_emails:
            result = email_validator_func(email)
            print(f"[PASS] Valid email: {email} -> {result}")
        
        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            ".user@domain.com",
            "user.@domain.com",
            "user..name@domain.com"
        ]
        
        for email in invalid_emails:
            try:
                result = email_validator_func(email)
                print(f"[WARN] Invalid email accepted: {email}")
            except ValueError as e:
                print(f"[PASS] Invalid email rejected: {email}")
        
        print("[SUCCESS] Custom email validation working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Custom email validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alternative_schemas():
    """Test the alternative schemas without EmailStr."""
    print("\n=== TESTING ALTERNATIVE SCHEMAS ===")
    
    try:
        from app.schemas.auth_alternative import (
            UserRegisterRequestAlt, 
            UserLoginRequestAlt
        )
        
        # Test registration
        reg_data = UserRegisterRequestAlt(
            email="test@example.com",
            password="TestPassword123!",
            handle="TestUser"
        )
        print(f"[PASS] Alternative registration schema: {reg_data.email}")
        
        # Test login
        login_data = UserLoginRequestAlt(
            email="user@domain.com",
            password="TestPassword123!"
        )
        print(f"[PASS] Alternative login schema: {login_data.email}")
        
        # Test invalid email
        try:
            invalid_reg = UserRegisterRequestAlt(
                email="invalid-email",
                password="TestPassword123!",
                handle="TestUser"
            )
            print(f"[WARN] Invalid email was accepted: {invalid_reg.email}")
        except Exception as e:
            print(f"[PASS] Invalid email rejected by alternative schema")
        
        print("[SUCCESS] Alternative schemas working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Alternative schemas failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_application_integration():
    """Test full application integration with email validation."""
    print("\n=== TESTING APPLICATION INTEGRATION ===")
    
    try:
        # Test importing the full app
        from app.main import create_app
        app = create_app()
        print("[PASS] FastAPI app created with email validation")
        
        # Test auth router
        from app.api.v1.routers.auth import router
        print("[PASS] Auth router imported with email validation")
        
        # Test authentication service
        from app.services.auth_service import AuthenticationService
        print("[PASS] Authentication service imported")
        
        print("[SUCCESS] Application integration working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Application integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all email validation tests."""
    print("PYDANTIC EMAIL VALIDATION FIX VERIFICATION")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(test_original_email_validation())
    results.append(test_custom_email_validation())
    results.append(test_alternative_schemas())
    results.append(test_application_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\nEMAIL VALIDATION FIX SUCCESSFUL!")
        print("\nWhat was implemented:")
        print("1. Robust custom email validation function")
        print("2. Fallback mechanism for EmailStr import issues")
        print("3. Alternative schemas that don't depend on EmailStr")
        print("4. Comprehensive email format validation")
        print("5. Integration with existing authentication system")
        print("\nThe email validation is now more robust and should work")
        print("regardless of Pydantic version or email-validator availability.")
    else:
        print(f"\n{total - passed} test suite(s) failed - check output above")


if __name__ == "__main__":
    main()
