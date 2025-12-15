"""
FastAPI Main Application

This is the entry point for the Steam Game Search Engine backend API.
It configures and initializes the FastAPI application with all necessary
middleware, routes, and lifecycle event handlers.

Features:
- RESTful API endpoints for game data
- CORS middleware for frontend integration
- Automatic API documentation (Swagger UI)
- Database connection management
- Health check endpoints

Startup Sequence:
1. Load configuration from environment variables
2. Initialize logging
3. Create FastAPI application instance
4. Configure CORS middleware
5. Register API routers
6. Connect to database on startup
7. Start Uvicorn server

Author: INST326 Project Team
Version: 0.1.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import db
from app.api.v1 import games, health, search, export
import logging

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# ============================================================================
# Lifespan Event Handler (Modern Approach)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan event handler for startup and shutdown
    
    This replaces the deprecated @app.on_event("startup") and 
    @app.on_event("shutdown") decorators.
    """
    # Startup
    logger.info("=" * 70)
    logger.info("🚀 Steam Game Search Engine API - Starting Up")
    logger.info("=" * 70)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    logger.info(f"Database: {settings.SUPABASE_URL}")
    logger.info(f"Schema: {settings.DATABASE_SCHEMA}")
    logger.info(f"Table: {settings.DATABASE_TABLE}")
    
    try:
        # Initialize database connection
        db.connect()
        logger.info("✅ Database connection established")
        
        # Perform health check
        if db.health_check():
            logger.info("✅ Database health check passed")
        else:
            logger.warning("⚠️ Database health check failed")
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application starting with database disconnected")
    
    logger.info("=" * 70)
    logger.info("✅ Application startup complete")
    logger.info("📚 API Documentation: http://{0}:{1}/docs".format(
        settings.BACKEND_HOST if settings.BACKEND_HOST != "0.0.0.0" else "localhost",
        settings.BACKEND_PORT
    ))
    logger.info("=" * 70)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("=" * 70)
    logger.info("👋 Steam Game Search Engine API - Shutting Down")
    logger.info("=" * 70)
    
    try:
        # Close database connection
        db.disconnect()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
    
    logger.info("✅ Application shutdown complete")
    logger.info("=" * 70)

# ============================================================================
# FastAPI Application Instance
# ============================================================================

app = FastAPI(
    title="Steam Game Search Engine API",
    description=(
        "RESTful API for Steam game data retrieval and search. "
        "Provides paginated game lists, detailed game information, "
        "and health monitoring endpoints."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,  # Use modern lifespan handler
    contact={
        "name": "INST326 Project Team",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================

# Enable CORS for frontend communication
# This allows the Next.js frontend (localhost:3000) to make API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

logger.info(f"✅ CORS enabled for origins: {settings.cors_origins_list}")


# ============================================================================
# API Router Registration
# ============================================================================

# Register API v1 routers
# All v1 endpoints will be prefixed with /api/v1

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health Check"]
)

app.include_router(
    games.router,
    prefix="/api/v1",
    tags=["Games"]
)

app.include_router(
    search.router,
    prefix="/api/v1",
    tags=["Search"]
)

app.include_router(
    export.router,
    prefix="/api/v1",
    tags=["Export"]
)

logger.info("✅ API routers registered")

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Root endpoint providing API information and available endpoints"
)
async def root():
    """
    API root endpoint
    
    Provides basic information about the API and links to documentation.
    Useful for verifying the API is running and accessible.
    
    Returns:
        dict: API information and links
    """
    return {
        "message": "Steam Game Search Engine API",
        "version": "0.1.0",
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "games_list": "/api/v1/games",
            "game_detail": "/api/v1/games/{game_id}"
        },
        "environment": settings.ENVIRONMENT
    }

# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application using Uvicorn ASGI server
    # This is used for development; in production, use:
    # uvicorn app.main:app --host 0.0.0.0 --port 8000
    
    logger.info("Starting Uvicorn server...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,  # Auto-reload on code changes in debug mode
        log_level=settings.LOG_LEVEL.lower()
    )

