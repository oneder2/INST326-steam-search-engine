"""
Steam Game Search Engine - API Routes
API路由模块，包含所有API端点路由

This module contains all API endpoint routes for the Steam Game Search Engine.
该模块包含Steam游戏搜索引擎的所有API端点路由。
"""

from .search import router as search_router
from .games import router as games_router
from .health import router as health_router

__all__ = [
    'search_router',
    'games_router',
    'health_router'
]