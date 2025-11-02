"""
Steam Game Search Engine - Mock Data Provider
模拟数据提供者类，用于替代数据库功能进行演示

This module provides mock data functionality to replace database operations
for demonstration purposes while maintaining the same interface.
"""

import json
import random
from typing import List, Optional, Dict, Any
import logging

from ..models import GameInfo
from ...config.constants import MOCK_GAMES_COUNT, SAMPLE_DEVELOPERS, SAMPLE_PUBLISHERS, POPULAR_GENRES

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class MockDataProvider:
    """
    模拟数据提供者类
    Mock data provider class to replace database functionality temporarily.
    
    这个类提供了与数据库相同的接口，但使用预定义的模拟数据。
    This class provides the same interface as database operations but uses predefined mock data.
    """
    
    def __init__(self):
        """
        初始化模拟数据提供者
        Initialize mock data provider with sample game data.
        """
        self.mock_games: List[GameInfo] = []
        self.games_by_id: Dict[int, GameInfo] = {}
        self._initialize_mock_data()
        logger.info(f"MockDataProvider initialized with {len(self.mock_games)} games")
    
    def _initialize_mock_data(self):
        """
        初始化模拟游戏数据
        Initialize mock game data with diverse examples.
        """
        # 创建多样化的游戏数据 / Create diverse game data
        mock_data = [
            # 动作游戏 / Action Games
            {
                'game_id': 1, 'title': 'Hades', 'price': 24.99,
                'description': 'A rogue-like dungeon crawler from the creators of Bastion and Transistor.',
                'genres': ['Action', 'Indie', 'RPG'], 'review_status': 'Overwhelmingly Positive',
                'deck_comp': True, 'coop_type': 'Single-player', 'developer': 'Supergiant Games',
                'publisher': 'Supergiant Games', 'release_date': '2020-09-17'
            },
            {
                'game_id': 2, 'title': 'Cyberpunk 2077', 'price': 59.99,
                'description': 'An open-world, action-adventure story set in Night City.',
                'genres': ['Action', 'RPG', 'Adventure'], 'review_status': 'Mixed',
                'deck_comp': False, 'coop_type': 'Single-player', 'developer': 'CD PROJEKT RED',
                'publisher': 'CD PROJEKT RED', 'release_date': '2020-12-10'
            },
            
            # 独立游戏 / Indie Games
            {
                'game_id': 3, 'title': 'Stardew Valley', 'price': 14.99,
                'description': 'A farming simulation game with RPG elements.',
                'genres': ['Indie', 'Simulation', 'RPG'], 'review_status': 'Overwhelmingly Positive',
                'deck_comp': True, 'coop_type': 'Local Co-op', 'developer': 'ConcernedApe',
                'publisher': 'ConcernedApe', 'release_date': '2016-02-26'
            },
            {
                'game_id': 4, 'title': 'Hollow Knight', 'price': 14.99,
                'description': 'A challenging 2D action-adventure through a vast ruined kingdom.',
                'genres': ['Action', 'Adventure', 'Indie'], 'review_status': 'Overwhelmingly Positive',
                'deck_comp': True, 'coop_type': 'Single-player', 'developer': 'Team Cherry',
                'publisher': 'Team Cherry', 'release_date': '2017-02-24'
            },
            
            # 策略游戏 / Strategy Games
            {
                'game_id': 5, 'title': 'Civilization VI', 'price': 59.99,
                'description': 'Build an empire to stand the test of time.',
                'genres': ['Strategy', 'Turn-based Strategy'], 'review_status': 'Very Positive',
                'deck_comp': True, 'coop_type': 'Online Multiplayer', 'developer': 'Firaxis Games',
                'publisher': '2K', 'release_date': '2016-10-21'
            },
            
            # 多人游戏 / Multiplayer Games
            {
                'game_id': 6, 'title': 'Among Us', 'price': 4.99,
                'description': 'Social deduction game for 4-15 players.',
                'genres': ['Action', 'Casual', 'Indie'], 'review_status': 'Very Positive',
                'deck_comp': True, 'coop_type': 'Online Multiplayer', 'developer': 'InnerSloth',
                'publisher': 'InnerSloth', 'release_date': '2018-06-15'
            },
            
            # 平台游戏 / Platform Games
            {
                'game_id': 7, 'title': 'Celeste', 'price': 19.99,
                'description': 'A challenging platformer about climbing a mountain.',
                'genres': ['Indie', 'Platformer', 'Adventure'], 'review_status': 'Overwhelmingly Positive',
                'deck_comp': True, 'coop_type': 'Single-player', 'developer': 'Maddy Makes Games',
                'publisher': 'Maddy Makes Games', 'release_date': '2018-01-25'
            },
            
            # 生存游戏 / Survival Games
            {
                'game_id': 8, 'title': 'Valheim', 'price': 19.99,
                'description': 'A brutal exploration and survival game for 1-10 players.',
                'genres': ['Survival', 'Action', 'Adventure'], 'review_status': 'Very Positive',
                'deck_comp': False, 'coop_type': 'Online Co-op', 'developer': 'Iron Gate AB',
                'publisher': 'Coffee Stain Publishing', 'release_date': '2021-02-02'
            },
            
            # 免费游戏 / Free Games
            {
                'game_id': 9, 'title': 'Dota 2', 'price': 0.0,
                'description': 'The most-played game on Steam. Every day, millions of players battle.',
                'genres': ['Action', 'Strategy', 'Free to Play'], 'review_status': 'Very Positive',
                'deck_comp': False, 'coop_type': 'Online Multiplayer', 'developer': 'Valve',
                'publisher': 'Valve', 'release_date': '2013-07-09'
            },
            
            # 沙盒游戏 / Sandbox Games
            {
                'game_id': 10, 'title': 'Terraria', 'price': 9.99,
                'description': 'Dig, fight, explore, build! The very world is at your fingertips.',
                'genres': ['Action', 'Adventure', 'Indie'], 'review_status': 'Overwhelmingly Positive',
                'deck_comp': True, 'coop_type': 'Local/Online Co-op', 'developer': 'Re-Logic',
                'publisher': 'Re-Logic', 'release_date': '2011-05-16'
            }
        ]
        
        # 添加手工制作的游戏数据 / Add hand-crafted game data
        for game_data in mock_data:
            game = GameInfo(**game_data)
            self.mock_games.append(game)
            self.games_by_id[game.game_id] = game
        
        # 生成额外的随机游戏数据 / Generate additional random game data
        self._generate_additional_games(MOCK_GAMES_COUNT - len(mock_data))
    
    def _generate_additional_games(self, count: int):
        """生成额外的随机游戏数据 / Generate additional random game data"""
        game_templates = [
            "Epic {genre} Adventure", "Ultimate {genre} Experience", "Legendary {genre} Quest",
            "Modern {genre} Simulator", "Classic {genre} Remastered", "Indie {genre} Masterpiece",
            "Next-Gen {genre} Game", "Retro {genre} Collection", "Premium {genre} Edition"
        ]
        
        descriptions = [
            "An immersive gaming experience with stunning visuals and engaging gameplay.",
            "A challenging adventure that will test your skills and determination.",
            "Experience the ultimate in gaming entertainment with this masterpiece.",
            "A beautifully crafted game with attention to detail and polish.",
            "Join millions of players in this exciting and addictive experience."
        ]
        
        for i in range(count):
            game_id = len(self.mock_games) + 1
            genre = random.choice(POPULAR_GENRES)
            title = random.choice(game_templates).format(genre=genre)
            
            # 确保标题唯一 / Ensure unique titles
            counter = 1
            original_title = title
            while any(game.title == title for game in self.mock_games):
                title = f"{original_title} {counter}"
                counter += 1
            
            game_data = {
                'game_id': game_id,
                'title': title,
                'price': round(random.uniform(0, 59.99), 2),
                'description': random.choice(descriptions),
                'genres': [genre] + random.sample(POPULAR_GENRES, random.randint(0, 2)),
                'review_status': random.choice([
                    'Overwhelmingly Positive', 'Very Positive', 'Positive',
                    'Mostly Positive', 'Mixed', 'Mostly Negative'
                ]),
                'deck_comp': random.choice([True, False]),
                'coop_type': random.choice([
                    'Single-player', 'Local Co-op', 'Online Co-op',
                    'Local Multiplayer', 'Online Multiplayer'
                ]),
                'developer': random.choice(SAMPLE_DEVELOPERS),
                'publisher': random.choice(SAMPLE_PUBLISHERS),
                'release_date': f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            }
            
            game = GameInfo(**game_data)
            self.mock_games.append(game)
            self.games_by_id[game.game_id] = game
    
    async def get_game_by_id(self, game_id: int) -> Optional[GameInfo]:
        """
        根据游戏ID获取单个游戏信息
        Retrieve a single game's information using its Steam game ID.
        
        Args:
            game_id (int): Steam游戏ID
            
        Returns:
            Optional[GameInfo]: 游戏信息对象，如果未找到则返回None
        """
        return self.games_by_id.get(game_id)
    
    async def get_games_by_ids(self, game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
        """
        批量获取多个游戏信息
        Efficiently retrieve multiple games using a list of Steam game IDs.
        
        Args:
            game_ids (List[int]): 游戏ID列表
            batch_size (int): 批处理大小（此处忽略，因为是内存操作）
            
        Returns:
            List[GameInfo]: 找到的游戏信息列表
        """
        return [self.games_by_id[game_id] for game_id in game_ids if game_id in self.games_by_id]
    
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
        if not title_query:
            return []
        
        query_lower = title_query.lower().strip()
        matches = []
        
        for game in self.mock_games:
            title_lower = game.title.lower()
            
            # 精确匹配 / Exact match
            if query_lower == title_lower:
                matches.append((game, 1.0))
            # 包含匹配 / Contains match
            elif query_lower in title_lower:
                matches.append((game, 0.8))
            # 模糊匹配 / Fuzzy match
            elif fuzzy and any(word in title_lower for word in query_lower.split()):
                matches.append((game, 0.6))
        
        # 按相关性排序 / Sort by relevance
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [game for game, score in matches[:limit]]
    
    async def get_game_count(self) -> int:
        """
        获取游戏总数
        Get the total number of games.
        
        Returns:
            int: 游戏总数
        """
        return len(self.mock_games)
    
    def get_all_games(self) -> List[GameInfo]:
        """
        获取所有游戏数据
        Get all game data for search indexing.
        
        Returns:
            List[GameInfo]: 所有游戏列表
        """
        return self.mock_games.copy()
