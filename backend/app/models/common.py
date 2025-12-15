"""
Common Data Models

This module contains shared Pydantic models used across the application,
including error responses, health check responses, and other common types.

Models:
- ErrorResponse: Standard error response structure
- HealthResponse: Health check endpoint response
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ErrorResponse(BaseModel):
    """
    Standard error response structure
    
    All API errors should return this structure for consistency.
    This matches the API contract specification (Section 4.2).
    
    Attributes:
        error_code (int): Application-specific error code
        message (str): Human-readable error message
        details (str): Additional error details or context
    """
    
    error_code: int = Field(..., description="Application-specific error code")
    message: str = Field(..., description="Human-readable error message")
    details: str = Field(default="", description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": 4001,
                "message": "Validation failed",
                "details": "Invalid query parameter: limit must be between 1 and 100"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response model
    
    Used by the /api/v1/health endpoint to report service status.
    
    Attributes:
        status (str): Overall service status (healthy/unhealthy)
        timestamp (str): ISO format timestamp of the check
        database (str): Database connection status (connected/disconnected)
        version (str): API version number
    """
    
    status: str = Field(..., description="Overall service status")
    timestamp: str = Field(..., description="ISO format timestamp")
    database: str = Field(..., description="Database connection status")
    version: str = Field(default="0.1.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-12-15T10:30:00.000Z",
                "database": "connected",
                "version": "0.1.0"
            }
        }


class PaginationMeta(BaseModel):
    """
    Pagination metadata
    
    Common pagination information used in list responses.
    
    Attributes:
        total (int): Total number of items available
        offset (int): Current offset (starting position)
        limit (int): Number of items per page
        has_more (bool): Whether more items are available
    """
    
    total: int = Field(..., ge=0, description="Total number of items")
    offset: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    
    @property
    def has_more(self) -> bool:
        """Check if more items are available after current page"""
        return self.offset + self.limit < self.total
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 50000,
                "offset": 0,
                "limit": 20
            }
        }

