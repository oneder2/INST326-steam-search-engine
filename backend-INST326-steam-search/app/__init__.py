"""
Steam Game Search Engine - Application Package
Steam游戏搜索引擎应用程序包

This package contains the complete Steam Game Search Engine application
with modular architecture including API, core business logic, data access,
utilities, and configuration.

该包包含完整的Steam游戏搜索引擎应用程序，采用模块化架构，
包括API、核心业务逻辑、数据访问、工具和配置。
"""

__version__ = "2.0.0"
__author__ = "INST326 Development Team"
__description__ = "Steam Game Search Engine with OOP Architecture"

# 导入主要组件 / Import main components
from .main import app
from .config.settings import get_settings
from .core import get_search_engine

__all__ = [
    'app',
    'get_settings',
    'get_search_engine'
]
