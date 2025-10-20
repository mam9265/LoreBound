"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from typing import Any, Dict, List
from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    app_env: str = Field(default="dev", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(alias="DATABASE_URL")
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    
    # Redis
    redis_url: str = Field(alias="REDIS_URL")
    
    # JWT
    jwt_algorithm: str = Field(default="RS256", alias="JWT_ALG")
    jwt_private_key_path: str = Field(alias="JWT_PRIVATE_KEY_PATH")
    jwt_public_key_path: str = Field(alias="JWT_PUBLIC_KEY_PATH")
    access_token_ttl_seconds: int = Field(default=900, alias="ACCESS_TOKEN_TTL_SECONDS")
    refresh_token_ttl_seconds: int = Field(default=1209600, alias="REFRESH_TOKEN_TTL_SECONDS")
    
    # Apple Sign-In (optional for development)
    apple_team_id: str = Field(default="", alias="APPLE_TEAM_ID")
    apple_client_id: str = Field(default="", alias="APPLE_CLIENT_ID")
    apple_key_id: str = Field(default="", alias="APPLE_KEY_ID")
    apple_private_key_path: str = Field(default="", alias="APPLE_PRIVATE_KEY_PATH")
    
    # Observability
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Game Config
    feature_flags_seed: int = Field(default=1, alias="FEATURE_FLAGS_SEED")
    content_version: int = Field(default=1, alias="CONTENT_VERSION")
    daily_challenge_reset_hour: int = Field(default=0, alias="DAILY_CHALLENGE_RESET_HOUR")
    
    # Security
    cors_origins: List[str] = Field(default=["*"], alias="CORS_ORIGINS")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # Background Jobs
    celery_broker_url: str = Field(alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(alias="CELERY_RESULT_BACKEND")
    
    # Computed properties for JWT keys
    @computed_field
    @property
    def jwt_private_key(self) -> str:
        """Load JWT private key from file."""
        try:
            with open(self.jwt_private_key_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            if self.app_env == "dev":
                # For development, create a simple key if missing
                return self._generate_dev_key()
            raise ValueError(f"JWT private key not found at {self.jwt_private_key_path}")
    
    @computed_field
    @property
    def jwt_public_key(self) -> str:
        """Load JWT public key from file."""
        try:
            with open(self.jwt_public_key_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            if self.app_env == "dev":
                # For development, derive from private key or create
                return self._generate_dev_public_key()
            raise ValueError(f"JWT public key not found at {self.jwt_public_key_path}")
    
    @computed_field
    @property
    def apple_private_key(self) -> str:
        """Load Apple Sign-In private key from file."""
        # Skip if no path provided (development mode)
        if not self.apple_private_key_path:
            return ""
        
        try:
            with open(self.apple_private_key_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            if self.app_env == "dev":
                # For development, this can be empty
                return ""
            raise ValueError(f"Apple private key not found at {self.apple_private_key_path}")
    
    def _generate_dev_key(self) -> str:
        """Generate a development JWT private key."""
        # This is only for development - in production, proper keys should be provided
        return """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA4qJfnOI1RuKjhkqgzDKPGH3mKZnrSNGw6jCc7ZmZcq3J7Yp2
nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3
mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ
8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZ
cq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQwIDAQABAoIBAQDQwV7Kl2KjYzYt
mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ
8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZ
cq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J
7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2
nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQAoGBAP0kl2KjYztmFiQ8YmZcq3J7Yp2nOJ3
mFiQ8YmZcq3J7Yp2nOJ3mFiQAoGBAP0kl2KjYztmFiQ8YmZcq3J7Yp2nOJ3mFiQ
8YmZcq3J7Yp2nOJ3mFiQAoGBAP0kl2KjYztmFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZ
cq3J7Yp2nOJ3mFiQAoGBAP0kl2KjYztmFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J
7Yp2nOJ3mFiQAoGBAP0kl2KjYztmFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2
nOJ3mFiQ
-----END RSA PRIVATE KEY-----"""
    
    def _generate_dev_public_key(self) -> str:
        """Generate a development JWT public key."""
        return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4qJfnOI1RuKjhkqgzDKP
GH3mKZnrSNGw6jCc7ZmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J
7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2
nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3
mFiQ8YmZcq3J7Yp2nOJ3mFiQ8YmZcq3J7Yp2nOJ3mFiQwIDAQAB
-----END PUBLIC KEY-----"""
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON string or comma-separated values
            if v.startswith('[') and v.endswith(']'):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith('redis://'):
            raise ValueError('REDIS_URL must be a Redis connection string')
        return v
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate the entire configuration setup."""
        validation_results = {
            "config_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required paths exist
        paths_to_check = []
        if self.app_env != "dev":
            paths_to_check = [
                self.jwt_private_key_path,
                self.jwt_public_key_path,
                self.apple_private_key_path
            ]
        
        for path in paths_to_check:
            if not os.path.exists(path):
                validation_results["errors"].append(f"Required file not found: {path}")
                validation_results["config_valid"] = False
        
        # Check environment-specific settings
        if self.app_env == "prod" and self.debug:
            validation_results["warnings"].append("Debug mode is enabled in production")
        
        if self.app_env == "prod" and self.sentry_dsn == "":
            validation_results["warnings"].append("Sentry DSN not configured for production")
        
        return validation_results
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Create settings instance
settings = Settings()


# Dependency function for FastAPI
def get_settings() -> Settings:
    """Get application settings instance."""
    return settings