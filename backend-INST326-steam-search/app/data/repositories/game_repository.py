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
    游戏仓库类 - 实现仓库模式
    Game repository class implementing the Repository pattern.
    
    这个类提供了统一的数据访问接口，可以在不同的数据提供者之间切换。
    This class provides a unified data access interface that can switch between different data providers.
    """
    
    def __init__(self, use_mock_data: bool = True):
        """
        初始化游戏仓库
        Initialize game repository with the specified data provider.
        
        Args:
            use_mock_data: 是否使用模拟数据，True使用MockDataProvider，False使用DatabaseProvider
        """
        self.use_mock_data = use_mock_data
        self.settings = get_settings()
        
        if use_mock_data:
            self.provider = MockDataProvider()
            logger.info("GameRepository initialized with MockDataProvider")
        else:
            self.provider = DatabaseProvider()
            logger.info("GameRepository initialized with DatabaseProvider")
    
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """
        根据游戏ID获取单个游戏信息
        Retrieve a single game's information using its Steam game ID.
        
        Args:
            game_id (int): Steam游戏ID
            
        Returns:
            Optional[GameInfo]: 游戏信息对象，如果未找到则返回None
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
            game_ids (List[int]): 游戏ID列表
            batch_size (int): 批处理大小
            
        Returns:
            List[GameInfo]: 找到的游戏信息列表
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
            title_query (str): 标题查询字符串
            limit (int): 最大结果数量
            fuzzy (bool): 是否启用模糊匹配
            
        Returns:
            List[GameInfo]: 匹配的游戏列表
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
            int: 游戏总数
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
            List[GameInfo]: 所有游戏列表
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
            filters: 过滤条件字典
            limit: 最大结果数量
            offset: 偏移量
            
        Returns:
            List[GameInfo]: 匹配的游戏列表
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
            limit: 最大结果数量
            
        Returns:
            List[GameInfo]: 热门游戏列表
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
            genre: 游戏类型
            limit: 最大结果数量
            
        Returns:
            List[GameInfo]: 指定类型的游戏列表
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
            limit: 最大结果数量
            
        Returns:
            List[GameInfo]: 免费游戏列表
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
        检查仓库健康状态
        Check repository health status.
        
        Returns:
            bool: 仓库是否健康
        """
        try:
            if hasattr(self.provider, 'check_database_health'):
                return await self.provider.check_database_health()
            else:
                # 对于模拟数据提供者，检查是否有数据 / For mock provider, check if data exists
                count = await self.get_game_count()
                return count > 0
        except Exception as e:
            logger.error(f"Repository health check failed: {str(e)}")
            return False
    
    def switch_provider(self, use_mock_data: bool):
        """
        切换数据提供者
        Switch data provider between mock and database.
        
        Args:
            use_mock_data: 是否使用模拟数据
        """
        if use_mock_data != self.use_mock_data:
            self.use_mock_data = use_mock_data
            
            if use_mock_data:
                self.provider = MockDataProvider()
                logger.info("Switched to MockDataProvider")
            else:
                self.provider = DatabaseProvider()
                logger.info("Switched to DatabaseProvider")


# 全局仓库实例 / Global repository instance
_game_repository: Optional[GameRepository] = None


def get_game_repository(use_mock_data: bool = True) -> GameRepository:
    """
    获取游戏仓库单例实例
    Get singleton instance of game repository.
    
    Args:
        use_mock_data: 是否使用模拟数据
        
    Returns:
        GameRepository: 游戏仓库实例
    """
    global _game_repository
    
    if _game_repository is None:
        _game_repository = GameRepository(use_mock_data)
    
    return _game_repository
