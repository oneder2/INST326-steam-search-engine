"""
Steam Game Search Engine - Data Models
数据模型模块

This module contains all data models and classes for the application.
该模块包含应用程序的所有数据模型和类。
"""

import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from ..config.constants import CoopType, Platform, ReviewStatus


@dataclass
class GameInfo:
    """
    游戏信息数据类 - 面向对象设计的核心数据模型
    Game information data class - Core data model for OOP design.

    这个类封装了游戏的所有基本信息，提供了数据验证、格式转换等功能。
    This class encapsulates all basic game information with data validation and format conversion.
    """
    
    # 基本信息 / Basic information
    game_id: int = 0
    title: str = ""
    description: str = ""
    price: float = 0.0
    
    # 分类信息 / Category information
    genres: List[str] = field(default_factory=list)
    coop_type: Optional[str] = None
    
    # 兼容性和状态 / Compatibility and status
    deck_comp: bool = False
    review_status: str = ""
    
    # 发布信息 / Release information
    release_date: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    
    def __post_init__(self):
        """初始化后验证数据 / Post-initialization data validation"""
        self.game_id = self._validate_game_id(self.game_id)
        self.title = self._validate_title(self.title)
        self.price = self._validate_price(self.price)
        self.genres = self._validate_genres(self.genres)
        self.coop_type = self._validate_coop_type(self.coop_type)
        self.review_status = self._validate_review_status(self.review_status)
    
    def _validate_game_id(self, game_id: Any) -> int:
        """验证游戏ID / Validate game ID"""
        try:
            id_val = int(game_id)
            if id_val <= 0:
                raise ValueError("Game ID must be positive")
            return id_val
        except (ValueError, TypeError):
            return 0
    
    def _validate_title(self, title: Any) -> str:
        """验证游戏标题 / Validate game title"""
        if not isinstance(title, str):
            return ""
        return title.strip()
    
    def _validate_price(self, price: Any) -> float:
        """验证价格 / Validate price"""
        try:
            price_val = float(price)
            return max(0.0, price_val)  # 价格不能为负 / Price cannot be negative
        except (ValueError, TypeError):
            return 0.0
    
    def _validate_genres(self, genres: Any) -> List[str]:
        """验证游戏类型 / Validate game genres"""
        if isinstance(genres, list):
            return [str(genre).strip() for genre in genres if genre]
        elif isinstance(genres, str):
            try:
                # 尝试解析JSON字符串 / Try to parse JSON string
                parsed = json.loads(genres)
                if isinstance(parsed, list):
                    return [str(genre).strip() for genre in parsed if genre]
            except json.JSONDecodeError:
                # 如果不是JSON，按逗号分割 / If not JSON, split by comma
                return [genre.strip() for genre in genres.split(',') if genre.strip()]
        return []
    
    def _validate_coop_type(self, coop_type: Any) -> Optional[str]:
        """验证合作类型 / Validate cooperation type"""
        if not coop_type:
            return None
        coop_str = str(coop_type).strip()
        # 检查是否为有效的合作类型 / Check if valid cooperation type
        valid_types = [e.value for e in CoopType]
        return coop_str if coop_str in valid_types else None
    
    def _validate_review_status(self, status: Any) -> str:
        """验证评价状态 / Validate review status"""
        if not isinstance(status, str):
            return ReviewStatus.NO_REVIEWS.value
        status_str = status.strip()
        # 检查是否为有效的评价状态 / Check if valid review status
        valid_statuses = [e.value for e in ReviewStatus]
        return status_str if status_str in valid_statuses else ReviewStatus.NO_REVIEWS.value
    
    def get_search_text(self) -> str:
        """
        获取用于搜索索引的文本
        Get text for search indexing combining title, description, and genres.
        
        Returns:
            str: 组合的搜索文本
        """
        # 组合标题、描述和类型用于搜索 / Combine title, description, and genres for search
        search_parts = [
            self.title,
            self.description,
            ' '.join(self.genres)
        ]
        
        # 过滤空值并连接 / Filter empty values and join
        return ' '.join(part for part in search_parts if part)
    
    def matches_filters(self, filters: Optional[Dict[str, Any]]) -> bool:
        """
        检查游戏是否匹配给定的过滤条件
        Check if the game matches the given filter criteria.
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            bool: 是否匹配过滤条件
        """
        if not filters:
            return True
        
        # 价格过滤 / Price filter
        if 'price_max' in filters:
            if self.price > filters['price_max']:
                return False
        
        if 'price_min' in filters:
            if self.price < filters['price_min']:
                return False
        
        # 合作类型过滤 / Cooperation type filter
        if 'coop_type' in filters:
            if self.coop_type != filters['coop_type']:
                return False
        
        # Steam Deck兼容性过滤 / Steam Deck compatibility filter
        if 'deck_compatible' in filters:
            if self.deck_comp != filters['deck_compatible']:
                return False
        
        # 类型过滤 / Genre filter
        if 'genres' in filters:
            required_genres = filters['genres']
            if isinstance(required_genres, list):
                # 检查是否包含任何所需类型 / Check if contains any required genre
                if not any(genre in self.genres for genre in required_genres):
                    return False
        
        # 评价状态过滤 / Review status filter
        if 'review_status' in filters:
            if self.review_status != filters['review_status']:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        Convert to dictionary format.
        
        Returns:
            Dict[str, Any]: 游戏信息字典
        """
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameInfo':
        """
        从字典创建GameInfo实例
        Create GameInfo instance from dictionary.
        
        Args:
            data: 游戏数据字典
            
        Returns:
            GameInfo: 游戏信息实例
        """
        return cls(**data)
    
    @classmethod
    def from_db_row(cls, row: Any) -> 'GameInfo':
        """
        从数据库行创建GameInfo实例
        Create GameInfo instance from database row.
        
        Args:
            row: 数据库行对象
            
        Returns:
            GameInfo: 游戏信息实例
        """
        # 处理不同类型的行对象 / Handle different types of row objects
        if hasattr(row, '_asdict'):  # namedtuple
            data = row._asdict()
        elif hasattr(row, 'keys'):  # sqlite3.Row
            data = dict(row)
        elif isinstance(row, (list, tuple)):  # 普通元组 / Regular tuple
            # 假设标准列顺序 / Assume standard column order
            columns = [
                'game_id', 'title', 'description', 'price', 'genres',
                'coop_type', 'deck_comp', 'review_status', 'release_date',
                'developer', 'publisher'
            ]
            data = dict(zip(columns, row))
        else:
            raise ValueError(f"Unsupported row type: {type(row)}")
        
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """字符串表示 / String representation"""
        return f"GameInfo(id={self.game_id}, title='{self.title}', price=${self.price})"
    
    def __repr__(self) -> str:
        """详细字符串表示 / Detailed string representation"""
        return (f"GameInfo(game_id={self.game_id}, title='{self.title}', "
                f"price={self.price}, genres={self.genres})")


@dataclass
class SearchResult:
    """
    搜索结果数据类
    Search result data class containing game info and relevance score.
    """
    game: GameInfo
    score: float = 0.0
    rank: int = 0
    search_type: str = "unknown"  # "bm25", "semantic", "fusion"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'game': self.game.to_dict(),
            'score': self.score,
            'rank': self.rank,
            'search_type': self.search_type
        }
