"""
Data Models Package

This package contains Pydantic models for data validation and serialization.
Models are organized by domain:
- game.py: Game-related data models
- common.py: Shared/common models (errors, health checks)

All models use Pydantic v2 for type validation and JSON serialization.
"""

from app.models.game import (
    GameListItem,
    GameListResponse,
    GameDetail
)
from app.models.common import (
    ErrorResponse,
    HealthResponse
)

__all__ = [
    "GameListItem",
    "GameListResponse",
    "GameDetail",
    "ErrorResponse",
    "HealthResponse",
]

