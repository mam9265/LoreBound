"""Security utilities for JWT, password hashing, and Apple Sign-In."""

import jwt
import httpx
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from uuid import UUID

from .config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        # Try direct bcrypt verification first
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Fallback to passlib
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    try:
        # Ensure password is within bcrypt limits (72 bytes)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes for bcrypt compatibility
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        # Use a simple approach that bypasses bcrypt version detection issues
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        # Fallback to passlib if direct bcrypt fails
        try:
            return pwd_context.hash(password)
        except Exception as fallback_error:
            logger.error(f"Fallback password hashing also failed: {fallback_error}")
            raise ValueError("Password hashing failed")


def create_access_token(
    subject: str, 
    scopes: Optional[list[str]] = None,
    user_id: Optional[UUID] = None
) -> str:
    """Create JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.access_token_ttl_seconds)
    
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "access"
    }
    
    if scopes:
        payload["scopes"] = scopes
    
    if user_id:
        payload["user_id"] = str(user_id)
    
    try:
        return jwt.encode(
            payload, 
            settings.jwt_private_key, 
            algorithm=settings.jwt_algorithm
        )
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise ValueError("Failed to create access token")


def create_refresh_token(subject: str, user_id: Optional[UUID] = None) -> str:
    """Create JWT refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.refresh_token_ttl_seconds)
    
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "refresh"
    }
    
    if user_id:
        payload["user_id"] = str(user_id)
    
    try:
        return jwt.encode(
            payload, 
            settings.jwt_private_key, 
            algorithm=settings.jwt_algorithm
        )
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise ValueError("Failed to create refresh token")


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_public_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            raise jwt.InvalidTokenError(f"Invalid token type, expected {token_type}")
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
            raise jwt.ExpiredSignatureError("Token has expired")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise jwt.InvalidTokenError("Token verification failed")


def extract_user_id_from_token(token: str) -> Optional[UUID]:
    """Extract user ID from JWT token."""
    try:
        payload = verify_token(token)
        user_id_str = payload.get("user_id")
        if user_id_str:
            return UUID(user_id_str)
        return None
    except Exception:
        return None


async def verify_apple_token(identity_token: str) -> Dict[str, Any]:
    """Verify Apple Sign-In identity token."""
    try:
        # In development, we can skip Apple token verification
        if settings.app_env == "dev" and not settings.apple_private_key:
            logger.warning("Skipping Apple token verification in development mode")
            # Return a mock payload for development
            return {
                "sub": "dev_apple_user",
                "email": "dev@example.com",
                "email_verified": True
            }
        
        # Fetch Apple's public keys
        jwks_url = "https://appleid.apple.com/auth/keys"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
        
        # Decode token header to get key ID
        unverified_header = jwt.get_unverified_header(identity_token)
        key_id = unverified_header.get("kid")
        
        if not key_id:
            raise ValueError("Token header missing key ID")
        
        # Find the matching public key
        public_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == key_id:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not public_key:
            raise ValueError("Unable to find matching public key")
        
        # Verify the token
        payload = jwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=settings.apple_client_id
        )
        
        # Validate issuer
        if payload.get("iss") != "https://appleid.apple.com":
            raise ValueError("Invalid token issuer")
        
        return payload
        
    except httpx.HTTPError as e:
        logger.error(f"Error fetching Apple JWKs: {e}")
        raise ValueError("Failed to fetch Apple verification keys")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid Apple token: {e}")
        raise ValueError("Invalid Apple identity token")
    except Exception as e:
        logger.error(f"Error verifying Apple token: {e}")
        raise ValueError("Apple token verification failed")


def generate_session_token() -> str:
    """Generate a secure session token for game runs."""
    import secrets
    import base64
    
    # Generate 32 random bytes and encode as base64
    token_bytes = secrets.token_bytes(32)
    return base64.b64encode(token_bytes).decode('utf-8')


def verify_session_hmac(
    data: str, 
    signature: str, 
    session_token: str
) -> bool:
    """Verify HMAC signature for game run anti-cheat."""
    import hmac
    import hashlib
    import base64
    
    try:
        # Create HMAC using session token as key
        expected = hmac.new(
            session_token.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Decode provided signature
        provided = base64.b64decode(signature)
        
        # Compare using secure comparison
        return hmac.compare_digest(expected, provided)
        
    except Exception as e:
        logger.error(f"Error verifying HMAC: {e}")
        return False


def create_session_hmac(data: str, session_token: str) -> str:
    """Create HMAC signature for game run data."""
    import hmac
    import hashlib
    import base64
    
    signature = hmac.new(
        session_token.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(signature).decode('utf-8')
