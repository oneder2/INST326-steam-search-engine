"""
Configuration Management Module

This module handles all application configuration settings, loading them from
environment variables. It uses Pydantic Settings for type-safe configuration
management with validation.

Key Configuration Areas:
- Supabase database connection (new-style keys)
- Server settings (host, port)
- CORS configuration
- Logging settings
- Database schema and table names

Environment Variables Required:
- SUPABASE_URL: Supabase project URL
- SUPABASE_SECRET_KEY: Backend service secret key (bypasses RLS)
- DATABASE_SCHEMA: Database schema name (default: steam)
- DATABASE_TABLE: Table name (default: games_prod)

TODO: Add rate limiting configuration
TODO: Add caching settings for future optimization
"""

from pydantic_settings import BaseSettings
from typing import List
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    This class uses Pydantic Settings to automatically load and validate
    configuration from environment variables or .env file.
    """
    
    # ========================================================================
    # Supabase Configuration (New-Style Keys)
    # ========================================================================
    
    SUPABASE_URL: str
    """Supabase project URL"""
    
    SUPABASE_PUBLISHABLE_KEY: str
    """Publishable key for client-side use (reference only, not used in backend)"""
    
    SUPABASE_SECRET_KEY: str
    """Secret key for backend service (bypasses RLS, full access)"""
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    DATABASE_SCHEMA: str = "steam"
    """Database schema name where tables are located"""
    
    DATABASE_TABLE: str = "games_prod"
    """Main games table name"""
    
    # ========================================================================
    # Server Configuration
    # ========================================================================
    
    BACKEND_HOST: str = "0.0.0.0"
    """Server host address (0.0.0.0 allows external connections)"""
    
    BACKEND_PORT: int = 8000
    """Server port number"""
    
    # ========================================================================
    # CORS Configuration
    # ========================================================================
    
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    """Comma-separated list of allowed CORS origins"""
    
    # ========================================================================
    # Application Configuration
    # ========================================================================
    
    ENVIRONMENT: str = "development"
    """Application environment (development/staging/production)"""
    
    DEBUG: bool = True
    """Enable debug mode"""
    
    LOG_LEVEL: str = "INFO"
    """Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)"""
    
    # ========================================================================
    # Configuration Class
    # ========================================================================
    
    class Config:
        """Pydantic configuration"""
        env_file = "../.env"
        case_sensitive = True
    
    # ========================================================================
    # Helper Properties
    # ========================================================================
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert CORS_ORIGINS string to list of origins
        
        Returns:
            List[str]: List of allowed CORS origins
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """
        Check if running in production environment
        
        Returns:
            bool: True if environment is production
        """
        return self.ENVIRONMENT.lower() == "production"


# ============================================================================
# Global Settings Instance
# ============================================================================

try:
    settings = Settings()
    logger.info(f"✅ Configuration loaded successfully (Environment: {settings.ENVIRONMENT})")
except Exception as e:
    logger.error(f"❌ Failed to load configuration: {e}")
    raise

