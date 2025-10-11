"""
Steam Game Search Engine - Database Access Module
数据库访问模块，提供SQLite数据库操作功能

This module provides database access functions for the Steam game data,
including game retrieval, batch operations, and connection management.
"""

import sqlite3
import json
import asyncio
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from config import get_settings

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()


class GameInfo:
    """
    游戏信息数据类
    Game information data class matching the database schema.
    """
    
    def __init__(self, **kwargs):
        """初始化游戏信息对象"""
        self.game_id: int = kwargs.get('game_id', 0)
        self.title: str = kwargs.get('title', '')
        self.description: str = kwargs.get('description', '')
        self.price: float = kwargs.get('price', 0.0)
        self.genres: List[str] = kwargs.get('genres', [])
        self.coop_type: Optional[str] = kwargs.get('coop_type')
        self.deck_comp: bool = kwargs.get('deck_comp', False)
        self.review_status: str = kwargs.get('review_status', '')
        self.release_date: Optional[str] = kwargs.get('release_date')
        self.developer: Optional[str] = kwargs.get('developer')
        self.publisher: Optional[str] = kwargs.get('publisher')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'game_id': self.game_id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'genres': self.genres,
            'coop_type': self.coop_type,
            'deck_comp': self.deck_comp,
            'review_status': self.review_status,
            'release_date': self.release_date,
            'developer': self.developer,
            'publisher': self.publisher
        }


@asynccontextmanager
async def get_db_connection():
    """
    获取数据库连接的异步上下文管理器
    Async context manager for database connections with proper error handling.
    
    Yields:
        sqlite3.Connection: 数据库连接对象
    """
    conn = None
    try:
        # 创建数据库连接 / Create database connection
        conn = sqlite3.connect(
            settings.get_database_path(),
            check_same_thread=False,
            timeout=settings.database_timeout
        )
        conn.row_factory = sqlite3.Row  # 启用列名访问 / Enable column name access
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


async def get_game_by_id(game_id: int) -> Optional[GameInfo]:
    """
    根据游戏ID获取单个游戏信息
    Retrieve a single game's information from the SQLite database using its Steam game ID.
    
    Args:
        game_id (int): Steam游戏ID
        
    Returns:
        Optional[GameInfo]: 游戏信息对象，如果未找到则返回None
    """
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 查询游戏信息 / Query game information
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
                logger.info(f"Game not found: {game_id}")
                return None
            
            # 转换数据库行为GameInfo对象 / Convert database row to GameInfo object
            game_data = {
                'game_id': row['game_id'],
                'title': row['title'],
                'description': row['description'],
                'price': row['price'],
                'genres': json.loads(row['genres']) if row['genres'] else [],
                'coop_type': row['coop_type'],
                'deck_comp': bool(row['deck_comp']),
                'review_status': row['review_status'],
                'release_date': row['release_date'],
                'developer': row['developer'],
                'publisher': row['publisher']
            }
            
            return GameInfo(**game_data)
            
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving game {game_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving game {game_id}: {str(e)}")
        return None


async def get_games_by_ids(game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
    """
    批量获取多个游戏信息
    Efficiently retrieve multiple games from the database using a list of Steam game IDs.
    
    Args:
        game_ids (List[int]): 游戏ID列表
        batch_size (int): 批处理大小，默认100
        
    Returns:
        List[GameInfo]: 找到的游戏信息列表
    """
    if not game_ids:
        return []
    
    try:
        all_games = []
        
        # 分批处理以避免SQL查询长度限制 / Process in batches to avoid SQL query length limits
        for i in range(0, len(game_ids), batch_size):
            batch_ids = game_ids[i:i + batch_size]
            batch_games = await _get_games_batch(batch_ids)
            all_games.extend(batch_games)
        
        logger.info(f"Retrieved {len(all_games)} games from {len(game_ids)} requested IDs")
        return all_games
        
    except Exception as e:
        logger.error(f"Error retrieving games by IDs: {str(e)}")
        return []


async def _get_games_batch(game_ids: List[int]) -> List[GameInfo]:
    """
    处理单个批次的游戏ID
    Process a single batch of game IDs.
    
    Args:
        game_ids (List[int]): 单个批次的游戏ID列表
        
    Returns:
        List[GameInfo]: 该批次找到的游戏信息列表
    """
    try:
        async with get_db_connection() as conn:
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
                game_data = {
                    'game_id': row['game_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'price': row['price'],
                    'genres': json.loads(row['genres']) if row['genres'] else [],
                    'coop_type': row['coop_type'],
                    'deck_comp': bool(row['deck_comp']),
                    'review_status': row['review_status'],
                    'release_date': row['release_date'],
                    'developer': row['developer'],
                    'publisher': row['publisher']
                }
                games.append(GameInfo(**game_data))
            
            return games
            
    except sqlite3.Error as e:
        logger.error(f"Database error in batch retrieval: {str(e)}")
        return []


async def search_games_by_title(title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
    """
    按标题搜索游戏，支持模糊匹配
    Search games by title with fuzzy matching support

    Args:
        title_query: 标题搜索查询
        limit: 最大返回结果数
        fuzzy: 是否启用模糊匹配

    Returns:
        List[GameInfo]: 匹配的游戏列表
    """
    try:
        if not title_query or not title_query.strip():
            return []

        # 清理和标准化查询 / Sanitize and normalize query
        clean_query = title_query.strip().lower()

        async with get_db_connection() as conn:
            cursor = conn.cursor()

            # 尝试精确和部分匹配 / Try exact and partial matches first
            exact_results = await _search_exact_title_matches(cursor, clean_query, limit)

            if len(exact_results) >= limit or not fuzzy:
                return exact_results[:limit]

            # 如果需要更多结果且启用模糊匹配 / If we need more results and fuzzy is enabled
            remaining_limit = limit - len(exact_results)
            fuzzy_results = await _search_fuzzy_title_matches(
                cursor, clean_query, remaining_limit, exact_results
            )

            # 合并并去重结果 / Combine and deduplicate results
            all_results = exact_results + fuzzy_results
            unique_results = _deduplicate_games(all_results)

            return unique_results[:limit]

    except Exception as e:
        logger.error(f"Error searching games by title '{title_query}': {str(e)}")
        return []


async def _search_exact_title_matches(cursor, query: str, limit: int) -> List[GameInfo]:
    """搜索精确和部分标题匹配 / Search for exact and partial title matches"""
    try:
        # 准备搜索模式 / Prepare search patterns
        exact_pattern = query
        partial_pattern = f"%{exact_pattern}%"
        word_pattern = f"%{exact_pattern.replace(' ', '%')}%"

        # 多种匹配策略的SQL查询 / SQL query with multiple matching strategies
        sql_query = """
        SELECT DISTINCT game_id, title, description, price, genres,
               coop_type, deck_comp, review_status, release_date,
               developer, publisher,
               CASE
                   WHEN LOWER(title) = ? THEN 1
                   WHEN LOWER(title) LIKE ? THEN 2
                   WHEN LOWER(title) LIKE ? THEN 3
                   ELSE 4
               END as match_priority
        FROM games
        WHERE LOWER(title) LIKE ?
        ORDER BY match_priority, title
        LIMIT ?
        """

        cursor.execute(sql_query, (
            exact_pattern,      # 精确匹配 / Exact match
            f"{exact_pattern}%", # 开头匹配 / Starts with
            partial_pattern,    # 包含匹配 / Contains
            word_pattern,       # 基于单词的匹配 / Word-based match
            limit
        ))

        rows = cursor.fetchall()
        return [_row_to_game_info(row) for row in rows]

    except Exception as e:
        logger.error(f"Error in exact title search: {str(e)}")
        return []


async def _search_fuzzy_title_matches(cursor, query: str, limit: int, exclude_games: List[GameInfo]) -> List[GameInfo]:
    """使用相似度算法搜索模糊标题匹配 / Search for fuzzy title matches using similarity algorithms"""
    try:
        # 获取要排除的现有游戏ID / Get existing game IDs to exclude
        exclude_ids = {game.game_id for game in exclude_games}

        # 获取所有游戏标题进行模糊匹配 / Get all game titles for fuzzy matching
        cursor.execute("SELECT game_id, title FROM games WHERE title IS NOT NULL")
        all_titles = cursor.fetchall()

        # 计算相似度分数 / Calculate similarity scores
        fuzzy_matches = []

        for game_id, title in all_titles:
            if game_id in exclude_ids:
                continue

            title_lower = title.lower()

            # 使用不同方法计算相似度 / Calculate similarity using different methods
            similarity = _calculate_title_similarity(query, title_lower)

            # 只包含相似度高于阈值的结果 / Only include if similarity is above threshold
            if similarity >= 0.6:  # 60%相似度阈值 / 60% similarity threshold
                fuzzy_matches.append((game_id, title, similarity))

        # 按相似度分数排序（降序）/ Sort by similarity score (descending)
        fuzzy_matches.sort(key=lambda x: x[2], reverse=True)

        # 获取顶部匹配的完整游戏信息 / Get full game info for top matches
        top_matches = fuzzy_matches[:limit]
        if not top_matches:
            return []

        # 获取完整游戏信息 / Fetch full game information
        game_ids = [match[0] for match in top_matches]
        placeholders = ','.join('?' * len(game_ids))

        cursor.execute(f"""
            SELECT game_id, title, description, price, genres,
                   coop_type, deck_comp, review_status, release_date,
                   developer, publisher
            FROM games
            WHERE game_id IN ({placeholders})
        """, game_ids)

        rows = cursor.fetchall()
        games_dict = {row[0]: _row_to_game_info(row) for row in rows}

        # 按相似度顺序返回游戏 / Return games in similarity order
        return [games_dict[game_id] for game_id, _, _ in top_matches if game_id in games_dict]

    except Exception as e:
        logger.error(f"Error in fuzzy title search: {str(e)}")
        return []


def _calculate_title_similarity(query: str, title: str) -> float:
    """计算标题相似度 / Calculate title similarity"""
    if not query or not title:
        return 0.0

    # 简单的基于单词重叠的相似度 / Simple word overlap-based similarity
    query_words = set(query.split())
    title_words = set(title.split())

    if not query_words or not title_words:
        return 0.0

    intersection = query_words.intersection(title_words)
    union = query_words.union(title_words)

    return len(intersection) / len(union) if union else 0.0


def _deduplicate_games(games: List[GameInfo]) -> List[GameInfo]:
    """基于game_id去除重复游戏 / Remove duplicate games based on game_id"""
    seen_ids = set()
    unique_games = []

    for game in games:
        if game.game_id not in seen_ids:
            seen_ids.add(game.game_id)
            unique_games.append(game)

    return unique_games


async def check_database_health() -> bool:
    """
    检查数据库健康状态
    Check database connectivity and basic functionality.
    
    Returns:
        bool: 数据库是否健康
    """
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 执行简单查询测试连接 / Execute simple query to test connection
            cursor.execute("SELECT COUNT(*) FROM games LIMIT 1")
            result = cursor.fetchone()
            
            return result is not None
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


async def get_game_count() -> int:
    """
    获取数据库中游戏总数
    Get the total number of games in the database.
    
    Returns:
        int: 游戏总数
    """
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM games")
            result = cursor.fetchone()
            return result[0] if result else 0
            
    except Exception as e:
        logger.error(f"Error getting game count: {str(e)}")
        return 0


async def search_games_by_title(title_pattern: str, limit: int = 10) -> List[GameInfo]:
    """
    根据标题模式搜索游戏（用于搜索建议）
    Search games by title pattern for search suggestions.
    
    Args:
        title_pattern (str): 标题搜索模式
        limit (int): 结果限制数量
        
    Returns:
        List[GameInfo]: 匹配的游戏列表
    """
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                game_id, title, description, price, genres,
                coop_type, deck_comp, review_status, release_date,
                developer, publisher
            FROM games 
            WHERE title LIKE ? 
            ORDER BY title
            LIMIT ?
            """
            
            cursor.execute(query, (f"%{title_pattern}%", limit))
            rows = cursor.fetchall()
            
            games = []
            for row in rows:
                game_data = {
                    'game_id': row['game_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'price': row['price'],
                    'genres': json.loads(row['genres']) if row['genres'] else [],
                    'coop_type': row['coop_type'],
                    'deck_comp': bool(row['deck_comp']),
                    'review_status': row['review_status'],
                    'release_date': row['release_date'],
                    'developer': row['developer'],
                    'publisher': row['publisher']
                }
                games.append(GameInfo(**game_data))
            
            return games
            
    except Exception as e:
        logger.error(f"Error searching games by title: {str(e)}")
        return []
