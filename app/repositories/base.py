"""Database base configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
import asyncio

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

# Create async engine with proper configuration
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_database_connection() -> bool:
    """Test database connection."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error("Database connection test failed: unexpected result")
                return False
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def wait_for_database(max_retries: int = 30, retry_delay: float = 1.0) -> bool:
    """Wait for database to become available."""
    logger.info("Waiting for database to become available...")
    
    for attempt in range(max_retries):
        if await test_database_connection():
            logger.info(f"Database is available after {attempt + 1} attempts")
            return True
        
        if attempt < max_retries - 1:
            logger.info(f"Database not available, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(retry_delay)
    
    logger.error(f"Database failed to become available after {max_retries} attempts")
    return False


async def create_tables():
    """Create all database tables."""
    from ..domain.models import Base
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def close_database_connection():
    """Close database connection pool."""
    try:
        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


async def get_database_info() -> dict:
    """Get database connection information."""
    try:
        async with engine.begin() as conn:
            # Get PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Get current database name
            result = await conn.execute(text("SELECT current_database()"))
            database = result.scalar()
            
            # Get connection count
            result = await conn.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ))
            connections = result.scalar()
            
            return {
                "version": version,
                "database": database,
                "active_connections": connections,
                "pool_size": engine.pool.size(),
                "checked_out_connections": engine.pool.checkedout(),
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}
