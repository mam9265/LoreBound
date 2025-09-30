"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import setup_logging, get_logger
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
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down LoreBound Backend...")
    await close_database_connection()
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
