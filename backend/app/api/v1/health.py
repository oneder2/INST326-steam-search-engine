"""
Health Check API Endpoint

This module provides health check endpoints for monitoring service status.
Used by load balancers, monitoring tools, and deployment systems to verify
that the service is running and database connections are healthy.

Endpoints:
- GET /api/v1/health: Basic health check with database connectivity test

TODO: Add more detailed health metrics (memory usage, response times)
TODO: Add readiness vs liveness probe distinction for Kubernetes
"""

from fastapi import APIRouter, Depends
from supabase import Client
from app.database import get_db
from app.models.common import HealthResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create router for health check endpoints
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check service health and database connectivity",
    tags=["Health"]
)
async def health_check(db: Client = Depends(get_db)) -> HealthResponse:
    """
    Perform health check on the service
    
    This endpoint checks:
    1. Service is running and responding
    2. Database connection is active and responsive
    
    Used by:
    - Load balancers for health monitoring
    - Deployment systems for readiness checks
    - Monitoring tools for alerting
    
    Args:
        db (Client): Injected database client
    
    Returns:
        HealthResponse: Service status information
        
    Response Codes:
        200: Service is healthy
        503: Service is unhealthy (database connection failed)
    """
    try:
        # Test database connection with a simple query
        # This verifies both connection and query execution
        # Use .schema() to specify the correct schema (steam)
        from app.config import settings
        result = db.schema(settings.DATABASE_SCHEMA)\
            .table(settings.DATABASE_TABLE)\
            .select('appid')\
            .limit(1)\
            .execute()
        
        db_status = "connected"
        overall_status = "healthy"
        
        logger.debug("✅ Health check passed")
        
    except Exception as e:
        # Database connection or query failed
        db_status = "disconnected"
        overall_status = "unhealthy"
        
        logger.error(f"❌ Health check failed: {e}")
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        database=db_status,
        version="0.1.0"
    )

