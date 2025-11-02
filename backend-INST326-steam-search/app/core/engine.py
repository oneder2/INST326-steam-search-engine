"""
Steam Game Search Engine - Main Controller
游戏搜索引擎主控制器类

This module provides the main controller class that orchestrates all search operations
and coordinates between different service components.
"""

import time
import logging
from typing import List, Optional, Dict, Any, Tuple

from ..config.settings import Settings, get_settings
from ..data import GameInfo, SearchResult, get_game_repository
from .search.service import SearchService
from .security.manager import SecurityManager
from .monitoring.health import HealthMonitor
from ..utils.logging import log_performance_metric, PerformanceTimer

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class GameSearchEngine:
    """
    游戏搜索引擎主控制器类
    Main controller class that orchestrates all search operations.
    
    这个类是整个搜索系统的核心，协调各个服务组件的工作。
    This class is the core of the entire search system, coordinating the work of various service components.
    """
    
    def __init__(self, config: Optional[Settings] = None):
        """
        初始化游戏搜索引擎
        Initialize game search engine with configuration.
        
        Args:
            config (Optional[Settings]): 应用程序配置，如果为None则使用默认配置
        """
        self.config = config or get_settings()
        self.initialized = False
        
        # 初始化各个服务组件 / Initialize service components
        self.game_repository = None
        self.search_service: Optional[SearchService] = None
        self.security_manager: Optional[SecurityManager] = None
        self.health_monitor: Optional[HealthMonitor] = None
        
        logger.info("GameSearchEngine created, awaiting initialization")
    
    async def initialize(self):
        """
        异步初始化搜索引擎
        Asynchronously initialize the search engine with all components.
        """
        if self.initialized:
            logger.warning("GameSearchEngine already initialized")
            return
        
        try:
            with PerformanceTimer("search_engine_initialization"):
                logger.info("Initializing GameSearchEngine components...")
                
                # 初始化数据仓库 / Initialize data repository
                self.game_repository = get_game_repository(use_mock_data=True)
                logger.info("Game repository initialized")
                
                # 初始化搜索服务 / Initialize search service
                self.search_service = SearchService(self.game_repository)
                await self.search_service.initialize()
                logger.info("Search service initialized")
                
                # 初始化安全管理器 / Initialize security manager
                self.security_manager = SecurityManager(self.config)
                logger.info("Security manager initialized")
                
                # 初始化健康监控器 / Initialize health monitor
                self.health_monitor = HealthMonitor(self.config)
                logger.info("Health monitor initialized")
                
                self.initialized = True
                logger.info("GameSearchEngine initialization completed successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize GameSearchEngine: {str(e)}")
            raise
    
    async def search_games(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[SearchResult], int]:
        """
        执行游戏搜索
        Execute game search with query and filters.
        
        Args:
            query (str): 搜索查询字符串
            filters (Optional[Dict[str, Any]]): 过滤条件
            limit (int): 结果数量限制
            offset (int): 结果偏移量
            
        Returns:
            Tuple[List[SearchResult], int]: 搜索结果列表和总数
        """
        if not self.initialized:
            raise RuntimeError("GameSearchEngine not initialized")
        
        with PerformanceTimer("game_search_operation"):
            # 安全验证 / Security validation
            validation_result = self.security_manager.validate_search_query(query)
            if not validation_result['is_valid']:
                logger.warning(f"Invalid search query rejected: {query}")
                return [], 0
            
            # 使用清理后的查询 / Use sanitized query
            clean_query = validation_result['sanitized_query']
            
            # 执行搜索 / Execute search
            search_results = await self.search_service.search_games(
                clean_query, filters, limit * 2  # 获取更多结果用于排序
            )
            
            # 应用分页 / Apply pagination
            total_count = len(search_results)
            paginated_results = search_results[offset:offset + limit]
            
            logger.info(f"Search completed: query='{clean_query}', results={total_count}")
            return paginated_results, total_count
    
    async def get_game_detail(self, game_id: int) -> Optional[GameInfo]:
        """
        获取游戏详细信息
        Get detailed game information by ID.
        
        Args:
            game_id (int): 游戏ID
            
        Returns:
            Optional[GameInfo]: 游戏信息，如果未找到则返回None
        """
        if not self.initialized:
            raise RuntimeError("GameSearchEngine not initialized")
        
        with PerformanceTimer("get_game_detail"):
            # 安全验证游戏ID / Security validation for game ID
            if not self.security_manager.validate_game_id(game_id):
                logger.warning(f"Invalid game ID rejected: {game_id}")
                return None
            
            # 从仓库获取游戏信息 / Get game info from repository
            game_info = await self.game_repository.get_game_by_id(game_id)
            
            if game_info:
                logger.info(f"Game detail retrieved: ID={game_id}, title='{game_info.title}'")
            else:
                logger.info(f"Game not found: ID={game_id}")
            
            return game_info
    
    async def get_search_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """
        获取搜索建议
        Get search suggestions based on input prefix.
        
        Args:
            prefix (str): 输入前缀
            limit (int): 建议数量限制
            
        Returns:
            List[str]: 搜索建议列表
        """
        if not self.initialized:
            raise RuntimeError("GameSearchEngine not initialized")
        
        with PerformanceTimer("get_search_suggestions"):
            # 安全验证前缀 / Security validation for prefix
            validation_result = self.security_manager.validate_search_query(prefix)
            if not validation_result['is_valid']:
                logger.warning(f"Invalid suggestion prefix rejected: {prefix}")
                return []
            
            # 使用清理后的前缀 / Use sanitized prefix
            clean_prefix = validation_result['sanitized_query']
            
            # 获取建议 / Get suggestions
            suggestions = await self.search_service.get_search_suggestions(clean_prefix, limit)
            
            logger.info(f"Search suggestions generated: prefix='{clean_prefix}', count={len(suggestions)}")
            return suggestions
    
    async def get_popular_games(self, limit: int = 10) -> List[GameInfo]:
        """
        获取热门游戏
        Get popular games based on ratings and other criteria.
        
        Args:
            limit (int): 结果数量限制
            
        Returns:
            List[GameInfo]: 热门游戏列表
        """
        if not self.initialized:
            raise RuntimeError("GameSearchEngine not initialized")
        
        with PerformanceTimer("get_popular_games"):
            popular_games = await self.game_repository.get_popular_games(limit)
            logger.info(f"Popular games retrieved: count={len(popular_games)}")
            return popular_games
    
    async def get_games_by_genre(self, genre: str, limit: int = 20) -> List[GameInfo]:
        """
        根据类型获取游戏
        Get games by specific genre.
        
        Args:
            genre (str): 游戏类型
            limit (int): 结果数量限制
            
        Returns:
            List[GameInfo]: 指定类型的游戏列表
        """
        if not self.initialized:
            raise RuntimeError("GameSearchEngine not initialized")
        
        with PerformanceTimer("get_games_by_genre"):
            # 安全验证类型 / Security validation for genre
            clean_genre = self.security_manager.sanitize_input(genre)
            
            genre_games = await self.game_repository.get_games_by_genre(clean_genre, limit)
            logger.info(f"Games by genre retrieved: genre='{clean_genre}', count={len(genre_games)}")
            return genre_games
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        获取系统健康状态
        Get system health status from all components.
        
        Returns:
            Dict[str, Any]: 健康状态信息
        """
        if not self.initialized:
            return {
                'status': 'unhealthy',
                'reason': 'not_initialized',
                'components': {}
            }
        
        return self.health_monitor.get_comprehensive_health_status()
    
    async def shutdown(self):
        """
        关闭搜索引擎
        Shutdown the search engine and cleanup resources.
        """
        if not self.initialized:
            return
        
        logger.info("Shutting down GameSearchEngine...")
        
        try:
            # 关闭各个组件 / Shutdown components
            if self.search_service:
                await self.search_service.shutdown()
            
            if self.health_monitor:
                self.health_monitor.stop_monitoring()
            
            self.initialized = False
            logger.info("GameSearchEngine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during GameSearchEngine shutdown: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取搜索引擎统计信息
        Get search engine statistics and metrics.
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.initialized:
            return {'status': 'not_initialized'}
        
        try:
            stats = {
                'initialized': self.initialized,
                'total_games': len(self.game_repository.get_all_games()) if self.game_repository else 0,
                'search_service_stats': self.search_service.get_statistics() if self.search_service else {},
                'security_stats': self.security_manager.get_statistics() if self.security_manager else {},
                'health_status': self.get_health_status()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {'error': str(e)}


# 全局搜索引擎实例 / Global search engine instance
_search_engine: Optional[GameSearchEngine] = None


def get_search_engine() -> GameSearchEngine:
    """
    获取搜索引擎单例实例
    Get singleton instance of search engine.
    
    Returns:
        GameSearchEngine: 搜索引擎实例
    """
    global _search_engine
    
    if _search_engine is None:
        _search_engine = GameSearchEngine()
    
    return _search_engine
