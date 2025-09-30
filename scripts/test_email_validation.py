#!/usr/bin/env python3
"""Test script to identify Pydantic email validation issues."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_email_validation():
    """Test Pydantic EmailStr validation."""
    print("Testing Pydantic EmailStr validation...")
    
    try:
        # Test basic EmailStr import
        from pydantic import BaseModel, EmailStr
        print("[PASS] EmailStr imported successfully")
        
        # Test schema with EmailStr
        class TestSchema(BaseModel):
            email: EmailStr
        
        # Test valid email
        test_data = TestSchema(email="test@example.com")
        print(f"[PASS] Valid email validation: {test_data.email}")
        
        # Test our actual auth schemas
        from app.schemas.auth import UserRegisterRequest, UserLoginRequest
        print("[PASS] Auth schemas imported successfully")
        
        # Test registration schema
        reg_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPassword123!",
            handle="TestUser"
        )
        print(f"[PASS] Registration schema validation: {reg_data.email}")
        
        # Test login schema
        login_data = UserLoginRequest(
            email="test@example.com",
            password="TestPassword123!"
        )
        print(f"[PASS] Login schema validation: {login_data.email}")
        
        print("[SUCCESS] All email validation tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Email validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alternative_email_validation():
    """Test alternative email validation approach."""
    print("\nTesting alternative email validation...")
    
    try:
        from pydantic import BaseModel, Field, field_validator
        import re
        
        class AlternativeEmailSchema(BaseModel):
            email: str = Field(..., description="Email address")
            
            @field_validator('email')
            @classmethod
            def validate_email(cls, v):
                # Simple email regex validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, v):
                    raise ValueError('Invalid email format')
                return v
        
        # Test with valid email
        test_data = AlternativeEmailSchema(email="test@example.com")
        print(f"[PASS] Alternative email validation: {test_data.email}")
        
        # Test with invalid email
        try:
            invalid_data = AlternativeEmailSchema(email="invalid-email")
            print("[FAIL] Should have rejected invalid email")
        except Exception:
            print("[PASS] Correctly rejected invalid email")
        
        print("[SUCCESS] Alternative email validation working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Alternative email validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("PYDANTIC EMAIL VALIDATION TEST")
    print("=" * 40)
    
    # Test current approach
    success1 = test_email_validation()
    
    # Test alternative approach
    success2 = test_alternative_email_validation()
    
    if success1:
        print("\nCurrent EmailStr validation is working correctly!")
    elif success2:
        print("\nWill provide alternative email validation solution.")
    else:
        print("\nBoth validation approaches failed - investigating...")
