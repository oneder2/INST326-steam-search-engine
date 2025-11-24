"""
Steam Game Search Engine - Database Provider
数据库提供者类，提供SQLite数据库访问功能

This module provides database access functions for the Steam game data,
including game retrieval, batch operations, and connection management.
"""

import sqlite3
import json
import asyncio
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import logging

from ..models import GameInfo
from ...config.settings import get_settings
from .base import DataProvider

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseProvider(DataProvider):
    """
    数据库提供者类 - 继承自 DataProvider
    Database provider class - inherits from DataProvider.
    
    这个类继承自抽象基类 DataProvider，实现了所有抽象方法。
    提供SQLite数据库访问的所有功能，包括连接管理、查询执行等。
    
    This class inherits from abstract base class DataProvider and implements all abstract methods.
    Provides all database access functionality including connection management and query execution.
    
    继承关系 / Inheritance Relationship:
    - 继承自: DataProvider (抽象基类)
    - Inherits from: DataProvider (abstract base class)
    - 实现了所有抽象方法，满足Liskov替换原则
    - Implements all abstract methods, satisfying Liskov Substitution Principle
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库提供者
        Initialize database provider with connection settings.
        
        调用父类构造函数，然后初始化数据库连接设置。
        Calls parent class constructor, then initializes database connection settings.
        
        Args:
            db_path: Database file path, if None uses path from settings
        """
        super().__init__()  # 调用父类构造函数 / Call parent class constructor
        self.db_path = db_path or settings.database_path
        self.connection_pool_size = settings.database_pool_size
        self._connection_pool = []
        logger.info(f"DatabaseProvider initialized with path: {self.db_path}")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        获取数据库连接的异步上下文管理器
        Async context manager for database connections with proper cleanup.
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            conn.row_factory = sqlite3.Row  # 启用列名访问 / Enable column name access
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """
        根据游戏ID获取单个游戏信息（实现抽象方法）
        Retrieve a single game's information using its Steam game ID (implements abstract method).
        
        这个方法实现了父类 DataProvider 中定义的抽象方法。
        This method implements the abstract method defined in parent class DataProvider.
        
        Args:
            game_id (int): Steam game ID
            
        Returns:
            Optional[GameInfo]: Game information object, or None if not found
        """
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    game_id, title, description, price, genres,
                    coop_type, deck_comp, review_status, release_date,
                    developer, publisher
                FROM games 
                WHERE game_id = ?
                """
                
                cursor.execute(query, (game_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return GameInfo.from_db_row(row)
                
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving game {game_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving game {game_id}: {str(e)}")
            return None
    
    async def get_games_by_ids(self, game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
        """
        批量获取多个游戏信息（实现抽象方法）
        Efficiently retrieve multiple games using a list of Steam game IDs (implements abstract method).
        
        这个方法实现了父类 DataProvider 中定义的抽象方法。
        This method implements the abstract method defined in parent class DataProvider.
        
        Args:
            game_ids (List[int]): List of game IDs
            batch_size (int): Batch size to avoid SQL query length limits
            
        Returns:
            List[GameInfo]: List of found game information objects
        """
        if not game_ids:
            return []
        
        try:
            all_games = []
            
            # 分批处理以避免SQL查询长度限制 / Process in batches to avoid SQL query length limits
            for i in range(0, len(game_ids), batch_size):
                batch_ids = game_ids[i:i + batch_size]
                batch_games = await self._get_games_batch(batch_ids)
                all_games.extend(batch_games)
            
            return all_games
            
        except Exception as e:
            logger.error(f"Error retrieving games by IDs: {str(e)}")
            return []
    
    async def _get_games_batch(self, game_ids: List[int]) -> List[GameInfo]:
        """处理单个批次的游戏ID / Process a single batch of game IDs"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建IN子句的占位符 / Create placeholders for IN clause
                placeholders = ','.join('?' * len(game_ids))
                
                query = f"""
                SELECT 
                    game_id, title, description, price, genres,
                    coop_type, deck_comp, review_status, release_date,
                    developer, publisher
                FROM games 
                WHERE game_id IN ({placeholders})
                ORDER BY game_id
                """
                
                cursor.execute(query, game_ids)
                rows = cursor.fetchall()
                
                games = []
                for row in rows:
                    try:
                        game = GameInfo.from_db_row(row)
                        games.append(game)
                    except Exception as e:
                        logger.warning(f"Error parsing game row: {str(e)}")
                        continue
                
                return games
                
        except sqlite3.Error as e:
            logger.error(f"Database error in batch retrieval: {str(e)}")
            return []
    
    async def search_games_by_title(self, title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
        """
        根据标题搜索游戏（实现抽象方法）
        Search games by title with optional fuzzy matching (implements abstract method).
        
        这个方法实现了父类 DataProvider 中定义的抽象方法。
        This method implements the abstract method defined in parent class DataProvider.
        
        Args:
            title_query (str): Title query string
            limit (int): Maximum number of results
            fuzzy (bool): Whether to enable fuzzy matching
            
        Returns:
            List[GameInfo]: List of matching games
        """
        if not title_query:
            return []
        
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if fuzzy:
                    # 模糊搜索使用LIKE / Fuzzy search using LIKE
                    query = """
                    SELECT 
                        game_id, title, description, price, genres,
                        coop_type, deck_comp, review_status, release_date,
                        developer, publisher
                    FROM games 
                    WHERE title LIKE ? 
                    ORDER BY 
                        CASE 
                            WHEN title = ? THEN 1
                            WHEN title LIKE ? THEN 2
                            ELSE 3
                        END,
                        title
                    LIMIT ?
                    """
                    
                    search_pattern = f"%{title_query}%"
                    exact_match = title_query
                    starts_with = f"{title_query}%"
                    
                    cursor.execute(query, (search_pattern, exact_match, starts_with, limit))
                else:
                    # 精确搜索 / Exact search
                    query = """
                    SELECT 
                        game_id, title, description, price, genres,
                        coop_type, deck_comp, review_status, release_date,
                        developer, publisher
                    FROM games 
                    WHERE title = ?
                    LIMIT ?
                    """
                    
                    cursor.execute(query, (title_query, limit))
                
                rows = cursor.fetchall()
                
                games = []
                for row in rows:
                    try:
                        game = GameInfo.from_db_row(row)
                        games.append(game)
                    except Exception as e:
                        logger.warning(f"Error parsing game row: {str(e)}")
                        continue
                
                return games
                
        except sqlite3.Error as e:
            logger.error(f"Database error in title search: {str(e)}")
            return []
    
    async def get_game_count(self) -> int:
        """
        获取游戏总数（实现抽象方法）
        Get the total number of games in the database (implements abstract method).
        
        这个方法实现了父类 DataProvider 中定义的抽象方法。
        This method implements the abstract method defined in parent class DataProvider.
        
        Returns:
            int: Total number of games
        """
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM games")
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except sqlite3.Error as e:
            logger.error(f"Database error getting game count: {str(e)}")
            return 0
    
    async def check_health(self) -> bool:
        """
        检查数据库健康状态（重写父类方法）
        Check database health and connectivity (overrides parent class method).
        
        重写父类的 check_health 方法，提供 DatabaseProvider 特定的健康检查逻辑。
        Overrides parent class check_health method, provides DatabaseProvider-specific health check logic.
        
        这展示了方法重写（method overriding）的使用。
        This demonstrates the use of method overriding.
        
        Returns:
            bool: Whether the database is healthy
        """
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    async def check_database_health(self) -> bool:
        """
        检查数据库健康状态（向后兼容的别名方法）
        Check database health and connectivity (backward-compatible alias method).
        
        这个方法保持向后兼容，实际调用重写的 check_health 方法。
        This method maintains backward compatibility, actually calls the overridden check_health method.
        
        Returns:
            bool: Whether the database is healthy
        """
        return await self.check_health()
    
    def get_all_games(self) -> List[GameInfo]:
        """
        获取所有游戏数据（实现抽象方法，同步方法，用于索引构建）
        Get all game data for search indexing (implements abstract method, synchronous method).
        
        这个方法实现了父类 DataProvider 中定义的抽象方法。
        This method implements the abstract method defined in parent class DataProvider.
        
        Returns:
            List[GameInfo]: List of all games
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
            SELECT 
                game_id, title, description, price, genres,
                coop_type, deck_comp, review_status, release_date,
                developer, publisher
            FROM games
            WHERE title IS NOT NULL AND description IS NOT NULL
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            games = []
            for row in rows:
                try:
                    game = GameInfo.from_db_row(row)
                    games.append(game)
                except Exception as e:
                    logger.warning(f"Error parsing game row: {str(e)}")
                    continue
            
            conn.close()
            return games
            
        except Exception as e:
            logger.error(f"Error loading all games: {str(e)}")
            return []
