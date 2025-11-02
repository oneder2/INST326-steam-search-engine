"""
Steam Game Search Engine - API Layer
API层模块，包含所有API路由、数据模式和中间件

This module contains all API layer components including routes, schemas, and middleware.
该模块包含所有API层组件，包括路由、数据模式和中间件。
"""

from .routes import search, games, health
from .schemas import search as search_schemas, game as game_schemas, common as common_schemas, health as health_schemas

__all__ = [
    # Routes / 路由
    'search',
    'games',
    'health',

    # Schemas / 数据模式
    'search_schemas',
    'game_schemas',
    'common_schemas',
    'health_schemas'
]