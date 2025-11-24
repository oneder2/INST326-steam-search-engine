"""
Steam Game Search Engine - Data Layer
数据层模块，包含数据模型、提供者和仓库

This module contains all data-related components including models, providers, and repositories.
该模块包含所有数据相关组件，包括模型、提供者和仓库。
"""

from .models import GameInfo, SearchResult
from .repositories.game_repository import GameRepository, get_game_repository
from .providers.base import DataProvider
from .providers.mock import MockDataProvider
from .providers.database import DatabaseProvider

__all__ = [
    'GameInfo',
    'SearchResult',
    'GameRepository',
    'get_game_repository',
    'DataProvider',
    'MockDataProvider',
    'DatabaseProvider'
]