#!/usr/bin/env python3
"""Configuration validation script."""

import asyncio
import sys
from pathlib import Path

# Add the app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.repositories.base import test_database_connection, get_database_info


async def validate_configuration():
    """Validate the entire application configuration."""
    setup_logging()
    logger = get_logger(__name__)
    
    print("🔧 LoreBound Backend Configuration Validation")
    print("=" * 50)
    
    # Validate settings
    print("\n1. 📋 Configuration Settings")
    validation_result = settings.validate_setup()
    
    if validation_result["config_valid"]:
        print("   ✅ Configuration is valid")
    else:
        print("   ❌ Configuration has errors:")
        for error in validation_result["errors"]:
            print(f"      - {error}")
    
    if validation_result["warnings"]:
        print("   ⚠️  Configuration warnings:")
        for warning in validation_result["warnings"]:
            print(f"      - {warning}")
    
    # Test JWT keys
    print("\n2. 🔑 JWT Configuration")
    try:
        private_key = settings.jwt_private_key
        public_key = settings.jwt_public_key
        if private_key and public_key:
            print("   ✅ JWT keys loaded successfully")
            print(f"   📄 Private key length: {len(private_key)} characters")
            print(f"   📄 Public key length: {len(public_key)} characters")
        else:
            print("   ❌ JWT keys not available")
    except Exception as e:
        print(f"   ❌ Error loading JWT keys: {e}")
    
    # Test Apple configuration
    print("\n3. 🍎 Apple Sign-In Configuration")
    try:
        apple_key = settings.apple_private_key
        if apple_key:
            print("   ✅ Apple private key loaded")
        else:
            print("   ⚠️  Apple private key not configured (OK for development)")
        print(f"   📋 Apple Team ID: {settings.apple_team_id}")
        print(f"   📋 Apple Client ID: {settings.apple_client_id}")
    except Exception as e:
        print(f"   ❌ Error with Apple configuration: {e}")
    
    # Test database connection
    print("\n4. 🗄️  Database Connection")
    try:
        db_connected = await test_database_connection()
        if db_connected:
            print("   ✅ Database connection successful")
            db_info = await get_database_info()
            if "error" not in db_info:
                print(f"   📋 Database: {db_info['database']}")
                print(f"   📋 Active connections: {db_info['active_connections']}")
                print(f"   📋 Pool size: {db_info['pool_size']}")
            else:
                print(f"   ⚠️  Could not get detailed database info: {db_info['error']}")
        else:
            print("   ❌ Database connection failed")
    except Exception as e:
        print(f"   ❌ Error testing database: {e}")
    
    # Test Redis connection (basic)
    print("\n5. 🔴 Redis Configuration")
    print(f"   📋 Redis URL: {settings.redis_url}")
    print("   ℹ️  Redis connection test not implemented yet")
    
    # Environment summary
    print("\n6. 🌍 Environment Summary")
    print(f"   📋 Environment: {settings.app_env}")
    print(f"   📋 Debug mode: {settings.debug}")
    print(f"   📋 API host: {settings.api_host}:{settings.api_port}")
    print(f"   📋 CORS origins: {settings.cors_origins}")
    print(f"   📋 Log level: {settings.log_level}")
    
    print("\n" + "=" * 50)
    
    if validation_result["config_valid"] and not validation_result["errors"]:
        print("🎉 Configuration validation completed successfully!")
        return True
    else:
        print("❌ Configuration validation failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(validate_configuration())
    sys.exit(0 if success else 1)
