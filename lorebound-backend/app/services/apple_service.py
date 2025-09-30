"""Apple Sign-In service for token verification."""

import logging
import jwt
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..core.config import Settings
from .exceptions import AppleSignInError

logger = logging.getLogger(__name__)


class AppleUserInfo(BaseModel):
    """Apple user information from verified token."""
    sub: str  # Apple's unique identifier for the user
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    is_private_email: Optional[bool] = None
    aud: str  # Audience (your app's client ID)
    iss: str  # Issuer (Apple)
    iat: int  # Issued at
    exp: int  # Expiration


class AppleSignInService:
    """Service for handling Apple Sign-In token verification."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.apple_public_keys = {}  # Cache for Apple's public keys
        self.keys_last_updated = None

    async def verify_identity_token(self, identity_token: str) -> AppleUserInfo:
        """
        Verify Apple identity token and return user information.
        
        In production, this would:
        1. Fetch Apple's public keys from https://appleid.apple.com/auth/keys
        2. Verify the JWT signature using Apple's public keys
        3. Validate the token claims (audience, issuer, expiration)
        4. Return the user information
        
        For development, we'll implement a simplified version.
        """
        logger.info("Verifying Apple identity token")

        try:
            if self.settings.app_env == "dev":
                # Development mode - simplified verification
                return await self._verify_token_dev_mode(identity_token)
            else:
                # Production mode - full verification with Apple's keys
                return await self._verify_token_production(identity_token)

        except Exception as e:
            logger.error(f"Apple token verification failed: {e}")
            raise AppleSignInError("Invalid Apple identity token")

    async def _verify_token_dev_mode(self, identity_token: str) -> AppleUserInfo:
        """
        Development mode token verification - simplified for testing.
        In dev mode, we'll decode without verification for testing purposes.
        """
        try:
            # Decode without verification for development
            payload = jwt.decode(
                identity_token, 
                options={"verify_signature": False, "verify_exp": False}
            )

            # Basic validation of required fields
            if not payload.get("sub"):
                raise AppleSignInError("Missing subject in token")

            if not payload.get("aud"):
                raise AppleSignInError("Missing audience in token")

            # Return user info
            return AppleUserInfo(
                sub=payload["sub"],
                email=payload.get("email"),
                email_verified=payload.get("email_verified"),
                is_private_email=payload.get("is_private_email"),
                aud=payload["aud"],
                iss=payload.get("iss", "https://appleid.apple.com"),
                iat=payload.get("iat", int(datetime.now(timezone.utc).timestamp())),
                exp=payload.get("exp", int(datetime.now(timezone.utc).timestamp()) + 3600)
            )

        except jwt.DecodeError as e:
            logger.error(f"Failed to decode Apple token in dev mode: {e}")
            raise AppleSignInError("Invalid token format")

    async def _verify_token_production(self, identity_token: str) -> AppleUserInfo:
        """
        Production mode token verification with Apple's public keys.
        This implements the full Apple Sign-In verification flow.
        """
        try:
            # Step 1: Decode token header to get key ID
            header = jwt.get_unverified_header(identity_token)
            key_id = header.get("kid")
            
            if not key_id:
                raise AppleSignInError("Missing key ID in token header")

            # Step 2: Get Apple's public key for this key ID
            public_key = await self._get_apple_public_key(key_id)

            # Step 3: Verify token signature and claims
            payload = jwt.decode(
                identity_token,
                public_key,
                algorithms=["RS256"],
                audience=self.settings.apple_client_id,
                issuer="https://appleid.apple.com"
            )

            # Step 4: Additional validations
            self._validate_token_claims(payload)

            # Step 5: Return user info
            return AppleUserInfo(
                sub=payload["sub"],
                email=payload.get("email"),
                email_verified=payload.get("email_verified"),
                is_private_email=payload.get("is_private_email"),
                aud=payload["aud"],
                iss=payload["iss"],
                iat=payload["iat"],
                exp=payload["exp"]
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Apple token has expired")
            raise AppleSignInError("Token has expired")
        except jwt.InvalidAudienceError:
            logger.warning("Invalid audience in Apple token")
            raise AppleSignInError("Invalid token audience")
        except jwt.InvalidIssuerError:
            logger.warning("Invalid issuer in Apple token")
            raise AppleSignInError("Invalid token issuer")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid Apple token: {e}")
            raise AppleSignInError("Invalid token")

    async def _get_apple_public_key(self, key_id: str) -> str:
        """
        Fetch Apple's public key for token verification.
        In production, this would fetch from Apple's JWKS endpoint.
        """
        # TODO: Implement actual fetching from Apple's JWKS endpoint
        # https://appleid.apple.com/auth/keys
        
        # For now, return a placeholder
        logger.warning("Apple public key fetching not implemented - using placeholder")
        
        # In production, you would:
        # 1. Check if we have cached keys and they're not expired
        # 2. If not, fetch from https://appleid.apple.com/auth/keys
        # 3. Parse the JWKS response and find the key with matching kid
        # 4. Convert to PEM format and return
        
        raise AppleSignInError("Apple public key verification not implemented")

    def _validate_token_claims(self, payload: dict) -> None:
        """Validate additional Apple token claims."""
        # Check if token is issued for our app
        if payload.get("aud") != self.settings.apple_client_id:
            raise AppleSignInError("Token not issued for this application")

        # Check issuer
        if payload.get("iss") != "https://appleid.apple.com":
            raise AppleSignInError("Invalid token issuer")

        # Check if token has required subject
        if not payload.get("sub"):
            raise AppleSignInError("Missing user identifier in token")

        # Check token age (Apple tokens are typically short-lived)
        iat = payload.get("iat")
        if iat:
            token_age = datetime.now(timezone.utc).timestamp() - iat
            if token_age > 3600:  # 1 hour
                logger.warning(f"Apple token is old: {token_age} seconds")

    async def generate_client_secret(self) -> str:
        """
        Generate client secret for Apple Sign-In API calls.
        This is used for server-to-server communication with Apple.
        """
        if not all([
            self.settings.apple_team_id,
            self.settings.apple_client_id,
            self.settings.apple_key_id,
            self.settings.apple_private_key
        ]):
            raise AppleSignInError("Apple Sign-In configuration incomplete")

        try:
            # Create JWT for client secret
            now = datetime.now(timezone.utc)
            payload = {
                "iss": self.settings.apple_team_id,
                "iat": int(now.timestamp()),
                "exp": int(now.timestamp()) + 3600,  # 1 hour
                "aud": "https://appleid.apple.com",
                "sub": self.settings.apple_client_id
            }

            # Sign with Apple private key
            client_secret = jwt.encode(
                payload,
                self.settings.apple_private_key,
                algorithm="ES256",
                headers={"kid": self.settings.apple_key_id}
            )

            return client_secret

        except Exception as e:
            logger.error(f"Failed to generate Apple client secret: {e}")
            raise AppleSignInError("Failed to generate client secret")


# Dependency for getting Apple service
def get_apple_service(settings: Settings) -> AppleSignInService:
    """Dependency to get Apple Sign-In service."""
    return AppleSignInService(settings)
