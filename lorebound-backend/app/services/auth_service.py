"""Authentication service for user registration, login, and token management."""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings
from ..core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from ..domain.enums import UserStatus
from ..domain.models import User
from ..repositories.user_repo import UserRepository
from ..schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AppleSignInRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
    AuthResponse
)
from .apple_service import AppleSignInService
from .exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    TokenExpiredError
)

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for handling user authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        apple_service: AppleSignInService,
        settings: Settings
    ):
        self.user_repo = user_repo
        self.apple_service = apple_service
        self.settings = settings

    async def register_user(
        self, 
        registration_data: UserRegisterRequest, 
        session: AsyncSession
    ) -> AuthResponse:
        """Register a new user with email and password."""
        logger.info(f"Attempting to register user with email: {registration_data.email}")

        # Normalize email to lowercase
        normalized_email = registration_data.email.lower().strip()

        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(normalized_email)
        if existing_user:
            logger.warning(f"Registration attempt for existing email: {normalized_email}")
            raise UserAlreadyExistsError("User with this email already exists")

        # Check if handle is already taken
        existing_handle = await self.user_repo.get_profile_by_handle(registration_data.handle)
        if existing_handle:
            logger.warning(f"Registration attempt for existing handle: {registration_data.handle}")
            raise UserAlreadyExistsError("Handle is already taken")

        try:
            # Hash password
            password_hash = get_password_hash(registration_data.password)

            # Create user
            user = await self.user_repo.create_user(
                email=normalized_email,
                password_hash=password_hash
            )
            
            # Create profile for the user
            await self.user_repo.create_profile(
                user_id=user.id,
                handle=registration_data.handle
            )

            # Update last login
            await self.user_repo.update_user_login_time(user.id)

            # Commit the transaction
            await session.commit()

            # Generate tokens
            tokens = self._generate_token_pair(user)

            logger.info(f"Successfully registered user: {user.id}")
            return AuthResponse(
                tokens=tokens,
                user=UserResponse.model_validate(user)
            )

        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            await session.rollback()
            raise AuthenticationError("Registration failed")

    async def login_user(
        self, 
        login_data: UserLoginRequest, 
        session: AsyncSession
    ) -> AuthResponse:
        """Authenticate user with email and password."""
        logger.info(f"Login attempt for email: {login_data.email}")

        # Normalize email to lowercase
        normalized_email = login_data.email.lower().strip()

        # Get user by email
        user = await self.user_repo.get_user_by_email(normalized_email)
        if not user:
            logger.warning(f"Login attempt for non-existent email: {normalized_email}")
            raise InvalidCredentialsError("Invalid email or password")

        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            logger.warning(f"Login attempt for inactive user: {user.id}")
            raise InvalidCredentialsError("Account is not active")

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Invalid password for user: {user.id}")
            raise InvalidCredentialsError("Invalid email or password")

        try:
            # Update last login
            await self.user_repo.update_user_login_time(user.id)

            # Commit the transaction
            await session.commit()

            # Generate tokens
            tokens = self._generate_token_pair(user)

            logger.info(f"Successfully logged in user: {user.id}")
            return AuthResponse(
                tokens=tokens,
                user=UserResponse.model_validate(user)
            )

        except Exception as e:
            logger.error(f"Failed to complete login for user {user.id}: {e}")
            await session.rollback()
            raise AuthenticationError("Login failed")

    async def apple_sign_in(
        self, 
        apple_data: AppleSignInRequest, 
        session: AsyncSession
    ) -> AuthResponse:
        """Authenticate or register user with Apple Sign-In."""
        logger.info("Apple Sign-In attempt")

        try:
            # Verify Apple token and get user info
            apple_user_info = await self.apple_service.verify_identity_token(
                apple_data.identity_token
            )

            # Check if user already exists
            user = await self.user_repo.get_user_by_apple_sub(apple_user_info.sub)

            if user:
                # Existing user - login
                logger.info(f"Apple Sign-In for existing user: {user.id}")
                
                # Check if user is active
                if user.status != UserStatus.ACTIVE:
                    logger.warning(f"Apple Sign-In attempt for inactive user: {user.id}")
                    raise InvalidCredentialsError("Account is not active")

                # Update last login
                await self.user_repo.update_user_login_time(user.id)

            else:
                # New user - register
                logger.info(f"Apple Sign-In for new user with sub: {apple_user_info.sub}")

                # Generate handle if not provided
                handle = apple_data.handle
                if not handle:
                    handle = f"Player_{apple_user_info.sub[:8]}"

                # Ensure handle is unique
                counter = 1
                original_handle = handle
                while await self.user_repo.get_profile_by_handle(handle):
                    handle = f"{original_handle}_{counter}"
                    counter += 1

                # Create user with Apple sub
                user = await self.user_repo.create_user(
                    apple_sub=apple_user_info.sub,
                    email=apple_user_info.email
                )
                
                # Create profile for the user
                await self.user_repo.create_profile(
                    user_id=user.id,
                    handle=handle
                )

                # Update last login
                await self.user_repo.update_user_login_time(user.id)

            # Commit the transaction
            await session.commit()

            # Generate tokens
            tokens = self._generate_token_pair(user)

            logger.info(f"Apple Sign-In successful for user: {user.id}")
            return AuthResponse(
                tokens=tokens,
                user=UserResponse.model_validate(user)
            )

        except Exception as e:
            logger.error(f"Apple Sign-In failed: {e}")
            await session.rollback()
            raise AuthenticationError("Apple Sign-In failed")

    async def refresh_token(
        self, 
        refresh_data: TokenRefreshRequest,
        session: AsyncSession
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        logger.info("Token refresh attempt")

        try:
            # Verify refresh token
            payload = verify_token(refresh_data.refresh_token, token_type="refresh")
            user_id = UUID(payload.get("user_id"))

            # Get user to ensure they still exist and are active
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Token refresh for non-existent user: {user_id}")
                raise InvalidCredentialsError("Invalid refresh token")

            if user.status != UserStatus.ACTIVE:
                logger.warning(f"Token refresh for inactive user: {user_id}")
                raise InvalidCredentialsError("Account is not active")

            # Generate new token pair
            tokens = self._generate_token_pair(user)

            logger.info(f"Token refresh successful for user: {user_id}")
            return tokens

        except TokenExpiredError:
            logger.warning("Token refresh attempted with expired token")
            raise InvalidCredentialsError("Refresh token has expired")
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("Token refresh failed")

    async def get_current_user(
        self, 
        access_token: str, 
        session: AsyncSession
    ) -> User:
        """Get current user from access token."""
        try:
            # Verify access token
            payload = verify_token(access_token, token_type="access")
            user_id = UUID(payload.get("user_id"))

            # Get user from database
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise InvalidCredentialsError("Invalid access token")

            if user.status != UserStatus.ACTIVE:
                raise InvalidCredentialsError("Account is not active")

            return user

        except Exception as e:
            logger.warning(f"Failed to get current user: {e}")
            raise InvalidCredentialsError("Invalid access token")

    def _generate_token_pair(self, user: User) -> TokenResponse:
        """Generate access and refresh token pair for user."""
        access_token = create_access_token(
            subject=user.email or user.apple_sub,
            user_id=user.id
        )
        
        refresh_token = create_refresh_token(
            subject=user.email or user.apple_sub,
            user_id=user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.settings.access_token_ttl_seconds
        )

    async def revoke_user_tokens(self, user_id: UUID, session: AsyncSession) -> None:
        """Revoke all tokens for a user (for logout/security purposes)."""
        # In a more sophisticated implementation, you would maintain a 
        # blacklist of tokens or token versions in Redis/database
        # For now, we'll just log the action
        logger.info(f"Token revocation requested for user: {user_id}")
        # TODO: Implement token blacklist in Redis


# Dependency for getting authentication service
async def get_auth_service(
    user_repo: UserRepository,
    apple_service: AppleSignInService,
    settings: Settings
) -> AuthenticationService:
    """Dependency to get authentication service."""
    return AuthenticationService(user_repo, apple_service, settings)
