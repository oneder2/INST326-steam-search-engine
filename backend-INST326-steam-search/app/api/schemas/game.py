"""
Steam Game Search Engine - Game API Schemas
游戏API数据模式定义

This module contains Pydantic models for game-related API requests and responses.
该模块包含游戏相关API请求和响应的Pydantic模型。
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...config.constants import CoopType, Platform, ReviewStatus


class GameInfo(BaseModel):
    """
    基础游戏信息模型
    Basic game information model for API responses.
    
    包含游戏基本信息的模型，用于API响应。
    Model containing basic game information for API responses.
    """
    game_id: int = Field(..., description="Steam游戏ID")
    title: str = Field(..., min_length=1, max_length=200, description="游戏标题")
    description: str = Field(..., description="游戏描述")
    price: float = Field(..., ge=0, le=1000, description="游戏价格（美元）")
    genres: List[str] = Field(default_factory=list, description="游戏类型列表")
    coop_type: Optional[str] = Field(None, description="合作游戏类型")
    deck_comp: bool = Field(default=False, description="Steam Deck兼容性")
    review_status: str = Field(..., description="评价状态")
    release_date: Optional[str] = Field(None, description="发布日期")
    developer: Optional[str] = Field(None, description="开发者")
    publisher: Optional[str] = Field(None, description="发行商")
    
    @validator('genres')
    def validate_genres(cls, v):
        """验证游戏类型列表 / Validate genres list"""
        if len(v) > 10:
            raise ValueError("游戏类型数量不能超过10个")
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """验证价格 / Validate price"""
        return round(v, 2)  # 保留两位小数
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "game_id": 12345,
                "title": "Epic Adventure Game",
                "description": "An amazing action-adventure game with stunning graphics and immersive gameplay",
                "price": 29.99,
                "genres": ["Action", "Adventure", "RPG"],
                "coop_type": "online",
                "deck_comp": True,
                "review_status": "Very Positive",
                "release_date": "2023-06-15",
                "developer": "Amazing Studios",
                "publisher": "Great Games Inc"
            }
        }


class GameDetailResponse(BaseModel):
    """
    游戏详细信息响应模型
    Game detail response model with comprehensive information.
    
    包含游戏详细信息的响应模型，用于游戏详情页面。
    Response model with comprehensive game information for game detail pages.
    """
    # 基础信息 / Basic information
    game_id: int = Field(..., description="Steam游戏ID")
    title: str = Field(..., description="游戏标题")
    description: str = Field(..., description="游戏描述")
    full_description: Optional[str] = Field(None, description="完整描述")
    price: float = Field(..., ge=0, description="游戏价格（美元）")
    
    # 分类信息 / Category information
    genres: List[str] = Field(default_factory=list, description="游戏类型列表")
    tags: Optional[List[str]] = Field(None, description="游戏标签")
    categories: Optional[List[str]] = Field(None, description="游戏分类")
    
    # 多人游戏信息 / Multiplayer information
    coop_type: Optional[str] = Field(None, description="合作游戏类型")
    multiplayer_support: Optional[Dict[str, Any]] = Field(None, description="多人游戏支持")
    
    # 平台兼容性 / Platform compatibility
    deck_comp: bool = Field(default=False, description="Steam Deck兼容性")
    supported_platforms: Optional[List[str]] = Field(None, description="支持的平台")
    system_requirements: Optional[Dict[str, Any]] = Field(None, description="系统要求")
    
    # 评价信息 / Review information
    review_status: str = Field(..., description="评价状态")
    review_summary: Optional[Dict[str, Any]] = Field(None, description="评价摘要")
    
    # 发布信息 / Release information
    release_date: Optional[str] = Field(None, description="发布日期")
    developer: Optional[str] = Field(None, description="开发者")
    publisher: Optional[str] = Field(None, description="发行商")
    
    # 媒体内容 / Media content
    screenshots: Optional[List[str]] = Field(None, description="游戏截图URL列表")
    videos: Optional[List[Dict[str, str]]] = Field(None, description="游戏视频信息")
    header_image: Optional[str] = Field(None, description="头图URL")
    
    # 额外信息 / Additional information
    additional_info: Optional[Dict[str, Any]] = Field(None, description="额外信息")
    last_updated: Optional[float] = Field(None, description="最后更新时间戳")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "game_id": 12345,
                "title": "Epic Adventure Game",
                "description": "Short description of the game",
                "full_description": "Detailed description with all features and gameplay mechanics...",
                "price": 29.99,
                "genres": ["Action", "Adventure", "RPG"],
                "tags": ["Singleplayer", "Story Rich", "Fantasy"],
                "coop_type": "online",
                "deck_comp": True,
                "supported_platforms": ["Windows", "Mac", "Linux"],
                "review_status": "Very Positive",
                "review_summary": {
                    "total_reviews": 15000,
                    "positive_percentage": 87
                },
                "release_date": "2023-06-15",
                "developer": "Amazing Studios",
                "publisher": "Great Games Inc",
                "screenshots": [
                    "https://example.com/screenshot1.jpg",
                    "https://example.com/screenshot2.jpg"
                ]
            }
        }


class GameReviewSummary(BaseModel):
    """
    游戏评价摘要模型
    Game review summary model for review statistics.
    
    游戏评价统计信息的摘要模型。
    Summary model for game review statistics.
    """
    game_id: int = Field(..., description="Steam游戏ID")
    overall_status: str = Field(..., description="总体评价状态")
    total_reviews: int = Field(..., ge=0, description="总评价数")
    positive_reviews: int = Field(..., ge=0, description="正面评价数")
    negative_reviews: int = Field(..., ge=0, description="负面评价数")
    positive_percentage: float = Field(..., ge=0, le=100, description="正面评价百分比")
    recent_reviews: Optional[str] = Field(None, description="近期评价状态")
    review_score: Optional[float] = Field(None, ge=0, le=10, description="评价分数")
    
    @validator('positive_percentage')
    def validate_percentage(cls, v):
        """验证百分比 / Validate percentage"""
        return round(v, 1)
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "game_id": 12345,
                "overall_status": "Very Positive",
                "total_reviews": 15000,
                "positive_reviews": 13050,
                "negative_reviews": 1950,
                "positive_percentage": 87.0,
                "recent_reviews": "Very Positive",
                "review_score": 8.7
            }
        }


class GameSearchResult(BaseModel):
    """
    游戏搜索结果模型
    Game search result model with relevance scoring.
    
    包含相关性评分的游戏搜索结果模型。
    Game search result model with relevance scoring information.
    """
    # 继承基础游戏信息 / Inherit basic game information
    game_id: int = Field(..., description="Steam游戏ID")
    title: str = Field(..., description="游戏标题")
    description: str = Field(..., description="游戏描述")
    price: float = Field(..., ge=0, description="游戏价格（美元）")
    genres: List[str] = Field(default_factory=list, description="游戏类型列表")
    coop_type: Optional[str] = Field(None, description="合作游戏类型")
    deck_comp: bool = Field(default=False, description="Steam Deck兼容性")
    review_status: str = Field(..., description="评价状态")
    
    # 搜索相关信息 / Search-related information
    relevance_score: float = Field(..., ge=0, le=1, description="总体相关性评分")
    bm25_score: float = Field(default=0.0, ge=0, description="BM25关键词匹配评分")
    semantic_score: float = Field(default=0.0, ge=0, le=1, description="语义相似度评分")
    quality_bonus: float = Field(default=0.0, ge=0, le=0.2, description="质量加成评分")
    
    # 匹配信息 / Match information
    matched_fields: Optional[List[str]] = Field(None, description="匹配的字段列表")
    highlighted_title: Optional[str] = Field(None, description="高亮标题")
    highlighted_description: Optional[str] = Field(None, description="高亮描述")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "game_id": 12345,
                "title": "Epic Adventure Game",
                "description": "An amazing action-adventure game",
                "price": 29.99,
                "genres": ["Action", "Adventure"],
                "coop_type": "online",
                "deck_comp": True,
                "review_status": "Very Positive",
                "relevance_score": 0.95,
                "bm25_score": 8.5,
                "semantic_score": 0.87,
                "quality_bonus": 0.1,
                "matched_fields": ["title", "description", "genres"],
                "highlighted_title": "Epic <mark>Adventure</mark> Game"
            }
        }


class GameListResponse(BaseModel):
    """
    游戏列表响应模型
    Game list response model for various game listing endpoints.
    
    用于各种游戏列表端点的响应模型。
    Response model for various game listing endpoints.
    """
    games: List[GameInfo] = Field(default_factory=list, description="游戏列表")
    total: int = Field(..., ge=0, description="游戏总数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页游戏数")
    has_next: bool = Field(default=False, description="是否有下一页")
    has_previous: bool = Field(default=False, description="是否有上一页")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "games": [
                    {
                        "game_id": 12345,
                        "title": "Epic Adventure Game",
                        "description": "An amazing game",
                        "price": 29.99,
                        "genres": ["Action", "Adventure"],
                        "review_status": "Very Positive"
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 20,
                "has_next": True,
                "has_previous": False
            }
        }


class GameStatsResponse(BaseModel):
    """
    游戏统计响应模型
    Game statistics response model for analytics.
    
    用于分析的游戏统计响应模型。
    Response model for game analytics and statistics.
    """
    total_games: int = Field(..., ge=0, description="游戏总数")
    games_by_genre: Dict[str, int] = Field(default_factory=dict, description="按类型分组的游戏数")
    games_by_price_range: Dict[str, int] = Field(default_factory=dict, description="按价格范围分组的游戏数")
    games_by_review_status: Dict[str, int] = Field(default_factory=dict, description="按评价状态分组的游戏数")
    average_price: float = Field(..., ge=0, description="平均价格")
    deck_compatible_count: int = Field(..., ge=0, description="Steam Deck兼容游戏数")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "total_games": 50,
                "games_by_genre": {
                    "Action": 15,
                    "Adventure": 12,
                    "RPG": 8
                },
                "games_by_price_range": {
                    "Free": 5,
                    "$1-$10": 15,
                    "$11-$30": 20,
                    "$31+": 10
                },
                "games_by_review_status": {
                    "Very Positive": 20,
                    "Positive": 15,
                    "Mixed": 10
                },
                "average_price": 24.99,
                "deck_compatible_count": 35
            }
        }
