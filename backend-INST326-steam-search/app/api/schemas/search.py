"""
Steam Game Search Engine - Search API Schemas
搜索API数据模式定义

This module contains Pydantic models for search-related API requests and responses.
该模块包含搜索相关API请求和响应的Pydantic模型。
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

from ...config.constants import CoopType, Platform


class SearchFilters(BaseModel):
    """
    搜索过滤器模型
    Search filters model for filtering game results.
    
    用于过滤游戏搜索结果的过滤器参数。
    Filter parameters for filtering game search results.
    """
    price_max: Optional[int] = Field(
        None, 
        ge=0, 
        le=1000, 
        description="最大价格（美元），0表示免费游戏"
    )
    coop_type: Optional[CoopType] = Field(
        None, 
        description="合作游戏类型过滤器"
    )
    platform: Optional[List[Platform]] = Field(
        None, 
        description="平台兼容性过滤器"
    )
    genres: Optional[List[str]] = Field(
        None, 
        description="游戏类型过滤器"
    )
    review_status: Optional[str] = Field(
        None, 
        description="评价状态过滤器"
    )
    deck_compatible: Optional[bool] = Field(
        None, 
        description="Steam Deck兼容性过滤器"
    )
    
    @validator('genres')
    def validate_genres(cls, v):
        """验证游戏类型列表 / Validate genres list"""
        if v is not None and len(v) > 5:
            raise ValueError("最多只能选择5个游戏类型")
        return v
    
    @validator('platform')
    def validate_platform(cls, v):
        """验证平台列表 / Validate platform list"""
        if v is not None and len(v) > 3:
            raise ValueError("最多只能选择3个平台")
        return v


class SearchQuerySchema(BaseModel):
    """
    搜索查询请求模型
    Search query request model for game search API.
    
    包含搜索查询字符串、过滤器和分页参数的请求模型。
    Request model containing search query string, filters, and pagination parameters.
    """
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="搜索查询字符串"
    )
    filters: Optional[SearchFilters] = Field(
        None, 
        description="搜索过滤器"
    )
    limit: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="每页结果数量"
    )
    offset: int = Field(
        default=0, 
        ge=0, 
        description="分页偏移量"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """验证搜索查询 / Validate search query"""
        # 移除多余空格 / Remove extra spaces
        v = ' '.join(v.split())
        
        # 检查是否为空 / Check if empty
        if not v.strip():
            raise ValueError("搜索查询不能为空")
        
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "query": "action adventure games",
                "filters": {
                    "price_max": 50,
                    "coop_type": "online",
                    "platform": ["windows", "linux"],
                    "genres": ["Action", "Adventure"],
                    "deck_compatible": True
                },
                "limit": 20,
                "offset": 0
            }
        }


class GameResult(BaseModel):
    """
    游戏搜索结果模型
    Game search result model for individual game in search results.
    
    搜索结果中单个游戏的信息模型。
    Information model for individual game in search results.
    """
    game_id: int = Field(..., description="Steam游戏ID")
    title: str = Field(..., description="游戏标题")
    description: str = Field(..., description="游戏描述")
    price: float = Field(..., ge=0, description="游戏价格（美元）")
    genres: List[str] = Field(default_factory=list, description="游戏类型列表")
    coop_type: Optional[str] = Field(None, description="合作游戏类型")
    deck_comp: bool = Field(default=False, description="Steam Deck兼容性")
    review_status: str = Field(..., description="评价状态")
    release_date: Optional[str] = Field(None, description="发布日期")
    developer: Optional[str] = Field(None, description="开发者")
    publisher: Optional[str] = Field(None, description="发行商")
    
    # 搜索相关字段 / Search-related fields
    relevance_score: float = Field(default=0.0, ge=0, le=1, description="相关性评分")
    bm25_score: float = Field(default=0.0, ge=0, description="BM25评分")
    semantic_score: float = Field(default=0.0, ge=0, le=1, description="语义相似度评分")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "game_id": 12345,
                "title": "Epic Adventure Game",
                "description": "An amazing action-adventure game with stunning graphics",
                "price": 29.99,
                "genres": ["Action", "Adventure", "RPG"],
                "coop_type": "online",
                "deck_comp": True,
                "review_status": "Very Positive",
                "release_date": "2023-06-15",
                "developer": "Amazing Studios",
                "publisher": "Great Games Inc",
                "relevance_score": 0.95,
                "bm25_score": 8.5,
                "semantic_score": 0.87
            }
        }


class GameResultSchema(BaseModel):
    """
    游戏搜索结果响应模型
    Game search results response model containing paginated results.
    
    包含分页搜索结果的响应模型。
    Response model containing paginated search results.
    """
    results: List[GameResult] = Field(
        default_factory=list, 
        description="搜索结果游戏列表"
    )
    total: int = Field(
        ..., 
        ge=0, 
        description="匹配的游戏总数"
    )
    offset: int = Field(
        ..., 
        ge=0, 
        description="当前分页偏移量"
    )
    limit: int = Field(
        ..., 
        ge=1, 
        le=100, 
        description="每页结果数量"
    )
    query: str = Field(
        ..., 
        description="原始搜索查询"
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="应用的过滤器"
    )
    search_time: Optional[float] = Field(
        None, 
        ge=0, 
        description="搜索耗时（秒）"
    )
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "results": [
                    {
                        "game_id": 12345,
                        "title": "Epic Adventure Game",
                        "description": "An amazing action-adventure game",
                        "price": 29.99,
                        "genres": ["Action", "Adventure"],
                        "coop_type": "online",
                        "deck_comp": True,
                        "review_status": "Very Positive",
                        "relevance_score": 0.95
                    }
                ],
                "total": 150,
                "offset": 0,
                "limit": 20,
                "query": "action adventure games",
                "filters": {"price_max": 50},
                "search_time": 0.125
            }
        }


class SearchSuggestionsResponse(BaseModel):
    """
    搜索建议响应模型
    Search suggestions response model for autocomplete functionality.
    
    自动完成功能的搜索建议响应模型。
    Response model for autocomplete functionality with search suggestions.
    """
    suggestions: List[str] = Field(
        default_factory=list, 
        description="搜索建议列表"
    )
    prefix: str = Field(
        ..., 
        description="输入的搜索前缀"
    )
    suggestion_types: Optional[Dict[str, List[str]]] = Field(
        None, 
        description="按类型分组的建议"
    )
    
    @validator('suggestions')
    def validate_suggestions(cls, v):
        """验证建议列表 / Validate suggestions list"""
        if len(v) > 20:
            raise ValueError("建议数量不能超过20个")
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "suggestions": [
                    "action games",
                    "action adventure",
                    "action rpg",
                    "action shooter",
                    "action platformer"
                ],
                "prefix": "action",
                "suggestion_types": {
                    "games": ["Action Game 1", "Action Game 2"],
                    "genres": ["Action", "Action-Adventure"],
                    "developers": ["Action Studios"]
                }
            }
        }


class SearchStatsResponse(BaseModel):
    """
    搜索统计响应模型
    Search statistics response model for analytics.
    
    用于分析的搜索统计响应模型。
    Response model for search analytics and statistics.
    """
    total_searches: int = Field(..., ge=0, description="总搜索次数")
    popular_queries: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="热门搜索查询"
    )
    average_response_time: float = Field(..., ge=0, description="平均响应时间")
    search_trends: Dict[str, Any] = Field(
        default_factory=dict, 
        description="搜索趋势数据"
    )
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        schema_extra = {
            "example": {
                "total_searches": 10000,
                "popular_queries": [
                    {"query": "action games", "count": 500},
                    {"query": "indie games", "count": 350}
                ],
                "average_response_time": 0.15,
                "search_trends": {
                    "daily_searches": 1000,
                    "peak_hour": "20:00"
                }
            }
        }
