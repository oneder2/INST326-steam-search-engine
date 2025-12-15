"""
Services Package

This package contains business logic services that handle data processing
and business rules. Services act as an intermediary between API routes and
the database layer.

Services:
- game_service.py: Game data retrieval and processing logic
"""

from app.services.game_service import GameService

__all__ = ["GameService"]

