"""Alternative email validation utilities for Pydantic schemas."""

import re
from typing import Any
from pydantic import field_validator


def email_validator_func(email: str) -> str:
    """
    Custom email validation function.
    
    This provides a fallback email validation that doesn't require external dependencies.
    """
    if not email:
        raise ValueError("Email is required")
    
    # Comprehensive email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email.strip()):
        raise ValueError("Invalid email format")
    
    # Additional validation rules
    email = email.strip().lower()
    
    # Check for common issues
    if email.startswith('.') or email.endswith('.'):
        raise ValueError("Email cannot start or end with a dot")
    
    if '..' in email:
        raise ValueError("Email cannot contain consecutive dots")
    
    # Check for dot before @ (invalid in local part)
    local_part, domain = email.split('@', 1)
    if local_part.endswith('.'):
        raise ValueError("Email local part cannot end with a dot")
    
    # Check length constraints
    if len(email) > 254:  # RFC 5321 limit
        raise ValueError("Email address is too long")
    
    local_part, domain = email.split('@', 1)
    
    if len(local_part) > 64:  # RFC 5321 limit
        raise ValueError("Email local part is too long")
    
    if len(domain) > 253:  # RFC 5321 limit
        raise ValueError("Email domain is too long")
    
    return email


def create_email_validator():
    """Create a Pydantic field validator for email addresses."""
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Any) -> str:
        """Validate email field."""
        if isinstance(v, str):
            return email_validator_func(v)
        else:
            raise ValueError("Email must be a string")
    
    return validate_email


# Decorator for easy use
def email_field_validator(field_name: str = 'email'):
    """Decorator to add email validation to a specific field."""
    
    def decorator(func):
        return field_validator(field_name)(func)
    
    return decorator
