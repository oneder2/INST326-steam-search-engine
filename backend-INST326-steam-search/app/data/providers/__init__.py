"""
Steam Game Search Engine - Data Providers
数据提供者模块

This module contains all data provider implementations, demonstrating
inheritance, polymorphism, and abstract base classes.
该模块包含所有数据提供者实现，展示继承、多态和抽象基类。
"""

from .base import DataProvider
from .mock import MockDataProvider
from .database import DatabaseProvider

__all__ = [
    'DataProvider',
    'MockDataProvider',
    'DatabaseProvider',
]

