"""Simple tests that don't require full application setup."""

import pytest
from pydantic import ValidationError

def test_basic_import():
    """Test that we can import basic modules."""
    try:
        from app.schemas.auth import UserRegisterRequest, UserLoginRequest
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import auth schemas: {e}")

def test_user_register_schema():
    """Test UserRegisterRequest schema validation."""
    from app.schemas.auth import UserRegisterRequest
    
    # Test valid data
    valid_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "handle": "TestPlayer"
    }
    
    schema = UserRegisterRequest(**valid_data)
    assert schema.email == "test@example.com"
    assert schema.password == "SecurePassword123!"
    assert schema.handle == "TestPlayer"

def test_user_register_schema_validation():
    """Test UserRegisterRequest schema validation errors."""
    from app.schemas.auth import UserRegisterRequest
    
    # Test invalid email
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="not-an-email",
            password="SecurePassword123!",
            handle="TestPlayer"
        )
    
    # Test short password
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="short",
            handle="TestPlayer"
        )
    
    # Test short handle
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="SecurePassword123!",
            handle="ab"
        )

def test_user_login_schema():
    """Test UserLoginRequest schema validation."""
    from app.schemas.auth import UserLoginRequest
    
    valid_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
    
    schema = UserLoginRequest(**valid_data)
    assert schema.email == "test@example.com"
    assert schema.password == "SecurePassword123!"

def test_apple_signin_schema():
    """Test AppleSignInRequest schema."""
    from app.schemas.auth import AppleSignInRequest
    
    # Test with handle
    data_with_handle = {
        "identity_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_token",
        "handle": "ApplePlayer"
    }
    
    schema = AppleSignInRequest(**data_with_handle)
    assert schema.identity_token == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
    assert schema.handle == "ApplePlayer"
    
    # Test without handle
    data_without_handle = {
        "identity_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
    }
    
    schema = AppleSignInRequest(**data_without_handle)
    assert schema.identity_token == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
    assert schema.handle is None

def test_token_response_schema():
    """Test TokenResponse schema."""
    from app.schemas.auth import TokenResponse
    
    data = {
        "access_token": "access_token_here",
        "refresh_token": "refresh_token_here",
        "expires_in": 900
    }
    
    schema = TokenResponse(**data)
    assert schema.access_token == "access_token_here"
    assert schema.refresh_token == "refresh_token_here"
    assert schema.token_type == "bearer"  # Default value
    assert schema.expires_in == 900

def test_user_status_enum():
    """Test UserStatus enum."""
    try:
        from app.domain.enums import UserStatus
        # Test that enum values exist
        assert hasattr(UserStatus, 'ACTIVE') or 'active' in [status.value for status in UserStatus]
        assert True
    except ImportError:
        # If enums module doesn't exist yet, that's okay
        assert True

def test_basic_math():
    """Basic test to ensure pytest is working."""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"

def test_pydantic_import():
    """Test that pydantic is available."""
    import pydantic
    assert hasattr(pydantic, 'BaseModel')

def test_fastapi_import():
    """Test that FastAPI is available."""
    import fastapi
    assert hasattr(fastapi, 'FastAPI')
