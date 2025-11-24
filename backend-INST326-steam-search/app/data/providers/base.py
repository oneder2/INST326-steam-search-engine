"""
Steam Game Search Engine - Data Provider Base Class
数据提供者抽象基类

This module defines the abstract base class for all data providers,
demonstrating inheritance and polymorphism in the OOP design.
该模块定义了所有数据提供者的抽象基类，展示OOP设计中的继承和多态。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging

from ..models import GameInfo

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """
    抽象数据提供者基类
    Abstract base class for all data providers.
    
    这个抽象基类定义了所有数据提供者必须实现的接口。
    使用继承和多态，允许系统在不同数据源之间切换。
    
    This abstract base class defines the interface that all data providers must implement.
    Using inheritance and polymorphism, allows the system to switch between different data sources.
    
    设计决策 / Design Decision:
    - 使用抽象基类而非接口，因为需要强制实现特定方法
    - Using abstract base class instead of interface, because we need to enforce specific method implementation
    - 所有数据提供者共享相同的行为契约
    - All data providers share the same behavioral contract
    """
    
    def __init__(self):
        """
        初始化数据提供者
        Initialize data provider.
        """
        self.provider_type = self.__class__.__name__
        logger.info(f"{self.provider_type} initialized")
    
    @abstractmethod
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """
        根据游戏ID获取单个游戏信息（抽象方法）
        Retrieve a single game's information using its Steam game ID (abstract method).
        
        所有派生类必须实现此方法。
        All derived classes must implement this method.
        
        Args:
            game_id (int): Steam game ID
            
        Returns:
            Optional[GameInfo]: Game information object, or None if not found
        """
        pass
    
    @abstractmethod
    async def get_games_by_ids(self, game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
        """
        批量获取多个游戏信息（抽象方法）
        Efficiently retrieve multiple games using a list of Steam game IDs (abstract method).
        
        所有派生类必须实现此方法。
        All derived classes must implement this method.
        
        Args:
            game_ids (List[int]): List of game IDs
            batch_size (int): Batch size for processing
            
        Returns:
            List[GameInfo]: List of found game information objects
        """
        pass
    
    @abstractmethod
    async def search_games_by_title(self, title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
        """
        根据标题搜索游戏（抽象方法）
        Search games by title with optional fuzzy matching (abstract method).
        
        所有派生类必须实现此方法。
        All derived classes must implement this method.
        
        Args:
            title_query (str): Title query string
            limit (int): Maximum number of results
            fuzzy (bool): Whether to enable fuzzy matching
            
        Returns:
            List[GameInfo]: List of matching games
        """
        pass
    
    @abstractmethod
    async def get_game_count(self) -> int:
        """
        获取游戏总数（抽象方法）
        Get the total number of games (abstract method).
        
        所有派生类必须实现此方法。
        All derived classes must implement this method.
        
        Returns:
            int: Total number of games
        """
        pass
    
    @abstractmethod
    def get_all_games(self) -> List[GameInfo]:
        """
        获取所有游戏数据（抽象方法）
        Get all game data for search indexing (abstract method).
        
        所有派生类必须实现此方法。
        All derived classes must implement this method.
        
        Returns:
            List[GameInfo]: List of all games
        """
        pass
    
    def get_provider_info(self) -> dict:
        """
        获取提供者信息（具体方法，所有派生类共享）
        Get provider information (concrete method, shared by all derived classes).
        
        这个方法展示了继承的优势：基类提供通用功能，派生类可以重写。
        This method demonstrates the advantage of inheritance: base class provides common functionality,
        derived classes can override.
        
        Returns:
            dict: Provider information dictionary
        """
        return {
            'provider_type': self.provider_type,
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__
        }
    
    async def check_health(self) -> bool:
        """
        检查提供者健康状态（具体方法，派生类可以重写）
        Check provider health status (concrete method, derived classes can override).
        
        这是一个模板方法模式的例子：基类定义算法骨架，派生类可以重写特定步骤。
        This is an example of Template Method pattern: base class defines algorithm skeleton,
        derived classes can override specific steps.
        
        Returns:
            bool: Whether the provider is healthy
        """
        try:
            count = await self.get_game_count()
            return count > 0
        except Exception as e:
            logger.error(f"Health check failed for {self.provider_type}: {str(e)}")
            return False

