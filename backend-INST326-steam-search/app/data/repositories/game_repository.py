"""
Steam Game Search Engine - Game Repository
游戏仓库类，实现仓库模式进行数据访问抽象

This module implements the Repository pattern to abstract data access operations.
该模块实现仓库模式来抽象数据访问操作。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
import logging

from ..models import GameInfo
from ..providers.base import DataProvider
from ..providers.mock import MockDataProvider
from ..providers.database import DatabaseProvider
from ...config.settings import get_settings

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class GameRepositoryInterface(Protocol):
    """
    游戏仓库接口协议
    Game repository interface protocol defining the contract for data access.
    """
    
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """根据ID获取游戏 / Get game by ID"""
        ...
    
    async def get_games_by_ids(self, game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
        """批量获取游戏 / Get games by IDs in batch"""
        ...
    
    async def search_games_by_title(self, title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
        """根据标题搜索游戏 / Search games by title"""
        ...
    
    async def get_game_count(self) -> int:
        """获取游戏总数 / Get total game count"""
        ...
    
    def get_all_games(self) -> List[GameInfo]:
        """获取所有游戏 / Get all games"""
        ...


class GameRepository:
    """
    游戏仓库类 - 实现仓库模式和组合关系
    Game repository class implementing the Repository pattern and composition relationship.
    
    这个类提供了统一的数据访问接口，可以在不同的数据提供者之间切换。
    使用组合关系（composition）包含 DataProvider 实例，而不是继承。
    
    This class provides a unified data access interface that can switch between different data providers.
    Uses composition relationship to contain DataProvider instance, rather than inheritance.
    
    组合关系 / Composition Relationship:
    - GameRepository "has-a" DataProvider (组合关系)
    - GameRepository "has-a" DataProvider (composition relationship)
    - 选择组合而非继承的原因：数据提供者是一个独立的组件，可以在运行时切换
    - Reason for choosing composition over inheritance: Data provider is an independent component
      that can be switched at runtime
    
    多态使用 / Polymorphism Usage:
    - provider 变量使用基类类型 DataProvider，但可以指向任何派生类实例
    - provider variable uses base class type DataProvider, but can point to any derived class instance
    - 运行时多态：根据 use_mock_data 参数，创建不同的派生类实例
    - Runtime polymorphism: Based on use_mock_data parameter, creates different derived class instances
    """
    
    def __init__(self, use_mock_data: bool = True):
        """
        初始化游戏仓库
        Initialize game repository with the specified data provider.
        
        使用多态：provider 变量声明为基类类型 DataProvider，
        但可以指向任何派生类（MockDataProvider 或 DatabaseProvider）的实例。
        
        Uses polymorphism: provider variable is declared as base class type DataProvider,
        but can point to instances of any derived class (MockDataProvider or DatabaseProvider).
        
        Args:
            use_mock_data: Whether to use mock data, True uses MockDataProvider, False uses DatabaseProvider
        """
        self.use_mock_data = use_mock_data
        self.settings = get_settings()
        
        # 多态：使用基类类型引用，但创建派生类实例
        # Polymorphism: Use base class type reference, but create derived class instances
        if use_mock_data:
            # 创建 MockDataProvider 实例，但类型为 DataProvider（基类）
            # Create MockDataProvider instance, but type is DataProvider (base class)
            self.provider: DataProvider = MockDataProvider()
            logger.info("GameRepository initialized with MockDataProvider (polymorphic)")
        else:
            # 创建 DatabaseProvider 实例，但类型为 DataProvider（基类）
            # Create DatabaseProvider instance, but type is DataProvider (base class)
            self.provider: DataProvider = DatabaseProvider()
            logger.info("GameRepository initialized with DatabaseProvider (polymorphic)")
    
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """
        根据游戏ID获取单个游戏信息
        Retrieve a single game's information using its Steam game ID.
        
        Args:
            game_id (int): Steam game ID
            
        Returns:
            Optional[GameInfo]: Game information object, or None if not found
        """
        try:
            return await self.provider.get_game_by_id(game_id)
        except Exception as e:
            logger.error(f"Error getting game by ID {game_id}: {str(e)}")
            return None
    
    async def get_games_by_ids(self, game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
        """
        批量获取多个游戏信息
        Efficiently retrieve multiple games using a list of Steam game IDs.
        
        Args:
            game_ids (List[int]): List of game IDs
            batch_size (int): Batch size for processing
            
        Returns:
            List[GameInfo]: List of found game information objects
        """
        try:
            return await self.provider.get_games_by_ids(game_ids, batch_size)
        except Exception as e:
            logger.error(f"Error getting games by IDs: {str(e)}")
            return []
    
    async def search_games_by_title(self, title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
        """
        根据标题搜索游戏
        Search games by title with optional fuzzy matching.
        
        Args:
            title_query (str): Title query string
            limit (int): Maximum number of results
            fuzzy (bool): Whether to enable fuzzy matching
            
        Returns:
            List[GameInfo]: List of matching games
        """
        try:
            return await self.provider.search_games_by_title(title_query, limit, fuzzy)
        except Exception as e:
            logger.error(f"Error searching games by title '{title_query}': {str(e)}")
            return []
    
    async def get_game_count(self) -> int:
        """
        获取游戏总数
        Get the total number of games.
        
        Returns:
            int: Total number of games
        """
        try:
            return await self.provider.get_game_count()
        except Exception as e:
            logger.error(f"Error getting game count: {str(e)}")
            return 0
    
    def get_all_games(self) -> List[GameInfo]:
        """
        获取所有游戏数据
        Get all game data for search indexing.
        
        Returns:
            List[GameInfo]: List of all games
        """
        try:
            return self.provider.get_all_games()
        except Exception as e:
            logger.error(f"Error getting all games: {str(e)}")
            return []
    
    async def get_games_by_filters(self, filters: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[GameInfo]:
        """
        根据过滤条件获取游戏
        Get games by filter criteria.
        
        Args:
            filters: Filter criteria dictionary
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List[GameInfo]: List of matching games
        """
        try:
            # 获取所有游戏并应用过滤器 / Get all games and apply filters
            all_games = self.get_all_games()
            
            # 应用过滤条件 / Apply filter conditions
            filtered_games = []
            for game in all_games:
                if game.matches_filters(filters):
                    filtered_games.append(game)
            
            # 应用分页 / Apply pagination
            start_idx = offset
            end_idx = offset + limit
            
            return filtered_games[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error getting games by filters: {str(e)}")
            return []
    
    async def get_popular_games(self, limit: int = 10) -> List[GameInfo]:
        """
        获取热门游戏
        Get popular games based on review status and other criteria.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List[GameInfo]: List of popular games
        """
        try:
            all_games = self.get_all_games()
            
            # 根据评价状态排序 / Sort by review status
            review_scores = {
                'Overwhelmingly Positive': 5,
                'Very Positive': 4,
                'Positive': 3,
                'Mostly Positive': 2,
                'Mixed': 1,
                'Mostly Negative': 0,
                'Negative': 0,
                'Very Negative': 0,
                'No Reviews': 0
            }
            
            # 按评价分数排序 / Sort by review score
            sorted_games = sorted(
                all_games,
                key=lambda game: review_scores.get(game.review_status, 0),
                reverse=True
            )
            
            return sorted_games[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular games: {str(e)}")
            return []
    
    async def get_games_by_genre(self, genre: str, limit: int = 20) -> List[GameInfo]:
        """
        根据类型获取游戏
        Get games by genre.
        
        Args:
            genre: Game genre
            limit: Maximum number of results
            
        Returns:
            List[GameInfo]: List of games in the specified genre
        """
        try:
            all_games = self.get_all_games()
            
            # 过滤指定类型的游戏 / Filter games by genre
            genre_games = [
                game for game in all_games
                if genre.lower() in [g.lower() for g in game.genres]
            ]
            
            return genre_games[:limit]
            
        except Exception as e:
            logger.error(f"Error getting games by genre '{genre}': {str(e)}")
            return []
    
    async def get_free_games(self, limit: int = 10) -> List[GameInfo]:
        """
        获取免费游戏
        Get free games (price = 0).
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List[GameInfo]: List of free games
        """
        try:
            all_games = self.get_all_games()
            
            # 过滤免费游戏 / Filter free games
            free_games = [game for game in all_games if game.price == 0.0]
            
            return free_games[:limit]
            
        except Exception as e:
            logger.error(f"Error getting free games: {str(e)}")
            return []
    
    async def check_health(self) -> bool:
        """
        检查仓库健康状态（演示多态调用）
        Check repository health status (demonstrates polymorphic call).
        
        这个方法展示了多态的优势：无论 provider 是 MockDataProvider 还是 DatabaseProvider，
        都可以调用相同的 check_health() 方法，但会执行不同的实现。
        
        This method demonstrates the advantage of polymorphism: regardless of whether provider
        is MockDataProvider or DatabaseProvider, can call the same check_health() method,
        but will execute different implementations.
        
        Returns:
            bool: Whether the repository is healthy
        """
        try:
            # 多态调用：调用基类方法，但实际执行的是派生类重写的实现
            # Polymorphic call: Call base class method, but actually executes derived class overridden implementation
            return await self.provider.check_health()
        except Exception as e:
            logger.error(f"Repository health check failed: {str(e)}")
            return False
    
    def switch_provider(self, use_mock_data: bool):
        """
        切换数据提供者（演示运行时多态）
        Switch data provider between mock and database (demonstrates runtime polymorphism).
        
        这个方法展示了运行时多态：可以在运行时切换不同的派生类实例，
        但代码使用相同的基类接口，无需修改调用代码。
        
        This method demonstrates runtime polymorphism: can switch between different derived class
        instances at runtime, but code uses the same base class interface, no need to modify calling code.
        
        Args:
            use_mock_data: Whether to use mock data
        """
        if use_mock_data != self.use_mock_data:
            self.use_mock_data = use_mock_data
            
            # 运行时多态：切换不同的派生类实例
            # Runtime polymorphism: Switch between different derived class instances
            if use_mock_data:
                self.provider: DataProvider = MockDataProvider()
                logger.info("Switched to MockDataProvider (polymorphic)")
            else:
                self.provider: DataProvider = DatabaseProvider()
                logger.info("Switched to DatabaseProvider (polymorphic)")


# 全局仓库实例 / Global repository instance
_game_repository: Optional[GameRepository] = None


def get_game_repository(use_mock_data: bool = True) -> GameRepository:
    """
    获取游戏仓库单例实例
    Get singleton instance of game repository.
    
    这个函数展示了多态的使用：根据参数创建不同的派生类实例，
    但返回的仓库对象使用相同的接口。
    
    This function demonstrates the use of polymorphism: creates different derived class instances
    based on parameters, but returned repository object uses the same interface.
    
    Args:
        use_mock_data: 是否使用模拟数据
        
    Returns:
        GameRepository: Game repository instance (internally uses polymorphic DataProvider)
    """
    global _game_repository
    
    if _game_repository is None:
        _game_repository = GameRepository(use_mock_data)
    
    return _game_repository
