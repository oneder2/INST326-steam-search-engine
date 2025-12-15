"""
Database Connection Management Module

This module manages the connection to Supabase PostgreSQL database using the
new-style secret key authentication. It provides a singleton database instance
that can be injected as a dependency in FastAPI routes.

Key Features:
- Singleton pattern for database connection
- Uses SUPABASE_SECRET_KEY for backend access (bypasses RLS)
- Connection health checking
- Dependency injection support for FastAPI

Connection Details:
- Database: Supabase PostgreSQL
- Schema: steam
- Main Table: games_prod
- Authentication: Service role key (full access)

TODO: Add connection pooling configuration
TODO: Add retry logic for connection failures
TODO: Add connection monitoring metrics
"""

from supabase import create_client, Client
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """
    Supabase database manager with singleton pattern
    
    This class manages the connection to Supabase database and provides
    a single client instance throughout the application lifecycle.
    
    Attributes:
        client (Client): Supabase client instance
        _instance (Database): Singleton instance
    """
    
    _instance: Optional['Database'] = None
    
    def __init__(self):
        """
        Initialize database manager
        
        Note: Use get_instance() for singleton access instead of direct instantiation
        """
        self.client: Optional[Client] = None
    
    @classmethod
    def get_instance(cls) -> 'Database':
        """
        Get singleton database instance
        
        Returns:
            Database: Singleton database instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def connect(self) -> Client:
        """
        Establish connection to Supabase database
        
        Uses SUPABASE_SECRET_KEY for backend service authentication.
        This key bypasses Row Level Security (RLS) and provides full access.
        
        Returns:
            Client: Connected Supabase client
            
        Raises:
            Exception: If connection fails
        """
        try:
            # Create Supabase client with secret key
            # This provides full access and bypasses RLS policies
            self.client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SECRET_KEY
            )
            
            logger.info("✅ Supabase database connected successfully")
            logger.info(f"   Database URL: {settings.SUPABASE_URL}")
            logger.info(f"   Schema: {settings.DATABASE_SCHEMA}")
            logger.info(f"   Table: {settings.DATABASE_TABLE}")
            
            return self.client
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_client(self) -> Client:
        """
        Get database client, connecting if necessary
        
        This method ensures the client is connected before returning it.
        If not connected, it will establish the connection first.
        
        Returns:
            Client: Supabase client instance
        """
        if not self.client:
            self.connect()
        return self.client
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy
        
        Performs a simple query to verify database connectivity.
        Uses the configured schema (steam) instead of default (public).
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            # Attempt a simple query to verify connection
            # Use .schema() to specify the steam schema
            result = self.client.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select('appid')\
                .limit(1)\
                .execute()
            
            logger.debug("✅ Database health check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from database
        
        Note: Supabase client doesn't require explicit disconnection,
        but this method is provided for completeness.
        """
        if self.client:
            self.client = None
            logger.info("Database connection closed")


# ============================================================================
# Global Database Instance
# ============================================================================

# Create global database instance using singleton pattern
db = Database.get_instance()


# ============================================================================
# FastAPI Dependency
# ============================================================================

def get_db() -> Client:
    """
    FastAPI dependency for database injection
    
    This function is used as a dependency in FastAPI routes to inject
    the database client. It ensures the client is connected and ready.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: Client = Depends(get_db)):
            # Use db client here
            pass
    
    Returns:
        Client: Connected Supabase client
    """
    return db.get_client()

