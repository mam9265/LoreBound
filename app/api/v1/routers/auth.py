"""Authentication endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_user, get_current_active_user
from ....repositories.base import get_session
from ....services.dependencies import get_auth_service_with_session
from ....services.auth_service import AuthenticationService
from ....services.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError, 
    InvalidCredentialsError,
    AppleSignInError
)
from ....schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AppleSignInRequest,
    TokenRefreshRequest,
    AuthResponse,
    TokenResponse,
    UserResponse
)
from ....domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    registration_data: UserRegisterRequest,
    service_session: tuple[AuthenticationService, AsyncSession] = Depends(get_auth_service_with_session)
) -> AuthResponse:
    """
    Register a new user with email and password.
    
    Returns authentication tokens and user information upon successful registration.
    """
    auth_service, session = service_session
    
    try:
        logger.info(f"Registration attempt for email: {registration_data.email}")
        result = await auth_service.register_user(registration_data, session)
        logger.info(f"User registration successful: {result.user.id}")
        return result
        
    except UserAlreadyExistsError as e:
        logger.warning(f"Registration failed - user exists: {registration_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLoginRequest,
    service_session: tuple[AuthenticationService, AsyncSession] = Depends(get_auth_service_with_session)
) -> AuthResponse:
    """
    Login with email and password.
    
    Returns authentication tokens and user information upon successful login.
    """
    auth_service, session = service_session
    
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        result = await auth_service.login_user(login_data, session)
        logger.info(f"User login successful: {result.user.id}")
        return result
        
    except InvalidCredentialsError:
        logger.warning(f"Login failed - invalid credentials: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed"
        )


@router.post("/apple", response_model=AuthResponse)
async def apple_signin(
    apple_data: AppleSignInRequest,
    service_session: tuple[AuthenticationService, AsyncSession] = Depends(get_auth_service_with_session)
) -> AuthResponse:
    """
    Sign in with Apple ID.
    
    Authenticates user with Apple identity token. Creates new account if user doesn't exist.
    """
    auth_service, session = service_session
    
    try:
        logger.info("Apple Sign-In attempt")
        result = await auth_service.apple_sign_in(apple_data, session)
        logger.info(f"Apple Sign-In successful: {result.user.id}")
        return result
        
    except AppleSignInError as e:
        logger.warning(f"Apple Sign-In failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Apple Sign-In failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apple Sign-In failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    service_session: tuple[AuthenticationService, AsyncSession] = Depends(get_auth_service_with_session)
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Returns new access and refresh tokens.
    """
    auth_service, session = service_session
    
    try:
        logger.info("Token refresh attempt")
        result = await auth_service.refresh_token(refresh_data, session)
        logger.info("Token refresh successful")
        return result
        
    except InvalidCredentialsError:
        logger.warning("Token refresh failed - invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    logger.info(f"User info request for user: {current_user.id}")
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    service_session: tuple[AuthenticationService, AsyncSession] = Depends(get_auth_service_with_session)
) -> dict:
    """
    Logout current user.
    
    Invalidates user tokens (placeholder for token blacklist implementation).
    """
    auth_service, session = service_session
    
    try:
        logger.info(f"Logout request for user: {current_user.id}")
        await auth_service.revoke_user_tokens(current_user.id, session)
        logger.info(f"User logout successful: {current_user.id}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
