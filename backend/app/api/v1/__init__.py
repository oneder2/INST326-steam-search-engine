"""
API Version 1 Package

This package contains all version 1 API endpoints.
Each module represents a different resource or functionality.

Available Routers:
- health: Health check and service status
- games: Game data retrieval
"""

from app.api.v1 import health, games

__all__ = ["health", "games"]

