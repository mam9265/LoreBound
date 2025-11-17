"""FastAPI application factory."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import setup_logging, get_logger
from .core.redis_client import redis_client
from .repositories.base import (
    wait_for_database, 
    close_database_connection,
    get_database_info,
    test_database_connection
)
from .api.v1.routers import (
    auth, content, runs, leaderboards, 
    profile, inventory, config_flags
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting LoreBound Backend...")
    
    # Validate configuration
    validation_result = settings.validate_setup()
    if not validation_result["config_valid"]:
        logger.error("Configuration validation failed:")
        for error in validation_result["errors"]:
            logger.error(f"  - {error}")
        raise RuntimeError("Invalid configuration")
    
    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            logger.warning(f"  - {warning}")
    
    # Wait for database
    if not await wait_for_database():
        raise RuntimeError("Database is not available")
    
    # Connect to Redis
    try:
        await redis_client.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}")
        # Don't fail startup if Redis is down - app can work without caching
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down LoreBound Backend...")
    await close_database_connection()
    await redis_client.disconnect()
    logger.info("✅ Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI instance
    app = FastAPI(
        title="LoreBound Backend",
        description="Production-ready FastAPI backend for LoreBound trivia RPG game",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom exception handler for validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors and return user-friendly messages."""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_type = error["type"]
            error_msg = error.get("msg", "")
            input_value = error.get("input")
            
            # Extract field name for cleaner messages
            field_name = field.split(" -> ")[-1] if " -> " in field else field
            field_lower = field.lower()
            
            # Create user-friendly error messages
            if "string_too_short" in error_type:
                min_length = error.get("ctx", {}).get("min_length", "unknown")
                if "password" in field_lower:
                    errors.append(f"Password must be at least {min_length} characters long")
                elif "handle" in field_lower or "username" in field_lower:
                    errors.append(f"Username must be at least {min_length} characters long")
                else:
                    errors.append(f"{field_name}: Must be at least {min_length} characters")
            elif "string_too_long" in error_type:
                max_length = error.get("ctx", {}).get("max_length", "unknown")
                if "password" in field_lower:
                    errors.append(f"Password must be no more than {max_length} characters long")
                elif "handle" in field_lower or "username" in field_lower:
                    errors.append(f"Username must be no more than {max_length} characters long")
                else:
                    errors.append(f"{field_name}: Must be no more than {max_length} characters")
            elif "value_error" in error_type:
                # Handle email validation errors
                if "email" in field_lower:
                    if "invalid email" in error_msg.lower() or "email format" in error_msg.lower():
                        errors.append("Please enter a valid email address")
                    else:
                        errors.append(f"Email: {error_msg}")
                else:
                    errors.append(f"{field_name}: {error_msg}")
            elif "missing" in error_type:
                if "email" in field_lower:
                    errors.append("Email is required")
                elif "password" in field_lower:
                    errors.append("Password is required")
                elif "handle" in field_lower or "username" in field_lower:
                    errors.append("Username is required")
                else:
                    errors.append(f"{field_name} is required")
            elif "type_error" in error_type:
                errors.append(f"{field_name}: Invalid format")
            else:
                # Fallback to generic message
                if "email" in field_lower and "email" not in error_msg.lower():
                    errors.append(f"Email: {error_msg}")
                else:
                    errors.append(f"{field_name}: {error_msg}")
        
        # Join all errors into a single message
        error_message = "; ".join(errors) if errors else "Validation error"
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": error_message,
                "errors": errors
            }
        )
    
    # Include API routers with v1 prefix
    app.include_router(auth.router, prefix="/v1")
    app.include_router(content.router, prefix="/v1")
    app.include_router(runs.router, prefix="/v1")
    app.include_router(leaderboards.router, prefix="/v1")
    app.include_router(profile.router, prefix="/v1")
    app.include_router(inventory.router, prefix="/v1")
    app.include_router(config_flags.router, prefix="/v1")
    
    # Health check endpoint
    @app.get("/healthz", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        # Test database connection
        db_healthy = await test_database_connection()
        
        health_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "version": "0.1.0",
            "environment": settings.app_env,
            "database": "connected" if db_healthy else "disconnected",
        }
        
        # Add detailed database info if connected
        if db_healthy:
            try:
                db_info = await get_database_info()
                if "error" not in db_info:
                    health_status["database_info"] = {
                        "database": db_info["database"],
                        "active_connections": db_info["active_connections"],
                    }
            except Exception:
                pass  # Don't fail health check if we can't get detailed info
        
        return health_status
    
    # Detailed health endpoint
    @app.get("/healthz/detailed", tags=["health"])
    async def detailed_health_check():
        """Detailed health check with configuration validation."""
        # Test database
        db_healthy = await test_database_connection()
        db_info = await get_database_info() if db_healthy else {"error": "not connected"}
        
        # Validate configuration
        config_validation = settings.validate_setup()
        
        return {
            "status": "healthy" if db_healthy and config_validation["config_valid"] else "unhealthy",
            "version": "0.1.0",
            "environment": settings.app_env,
            "timestamp": "2024-01-01T00:00:00Z",  # Will be actual timestamp
            "database": {
                "connected": db_healthy,
                "info": db_info
            },
            "configuration": {
                "valid": config_validation["config_valid"],
                "errors": config_validation["errors"],
                "warnings": config_validation["warnings"]
            },
            "jwt": {
                "algorithm": settings.jwt_algorithm,
                "keys_loaded": bool(settings.jwt_private_key and settings.jwt_public_key)
            }
        }
    
    # Metrics endpoint placeholder
    @app.get("/metrics", tags=["monitoring"])
    async def metrics():
        """Prometheus metrics endpoint."""
        return {"metrics": "placeholder"}
    
    return app


# Create app instance
app = create_app()
