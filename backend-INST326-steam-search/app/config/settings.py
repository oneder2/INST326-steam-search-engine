"""
Steam Game Search Engine - Configuration Settings
配置管理模块，用于处理环境变量和应用程序设置

This module handles all configuration settings for the FastAPI backend,
including database connections, search indices, and API parameters.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    应用程序配置类
    Application settings class using Pydantic for validation and type checking.
    """
    
    # ============================================================================
    # 服务器配置 / Server Configuration
    # ============================================================================
    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=8000, description="服务器端口")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    reload: bool = Field(default=False, description="自动重载")
    
    # ============================================================================
    # API配置 / API Configuration
    # ============================================================================
    api_title: str = Field(default="Steam Game Search Engine API", description="API标题")
    api_version: str = Field(default="2.0.0", description="API版本")
    api_description: str = Field(default="Python FastAPI backend for intelligent game search", description="API描述")
    
    # ============================================================================
    # CORS配置 / CORS Configuration
    # ============================================================================
    cors_origins: str = Field(
        default="http://localhost:3000,https://steam-search-frontend.onrender.com",
        description="允许的CORS源，逗号分隔"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """返回CORS源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # ============================================================================
    # 数据库配置 / Database Configuration
    # ============================================================================
    database_url: str = Field(default="sqlite:///data/games_data.db", description="数据库连接URL")
    database_timeout: float = Field(default=30.0, description="数据库连接超时时间")
    
    def get_database_path(self) -> str:
        """获取数据库文件路径"""
        if self.database_url.startswith("sqlite:///"):
            return self.database_url[10:]  # 移除 "sqlite:///" 前缀
        return "data/games_data.db"  # 默认路径
    
    # ============================================================================
    # 搜索配置 / Search Configuration
    # ============================================================================
    max_search_results: int = Field(default=100, description="最大搜索结果数")
    default_search_limit: int = Field(default=20, description="默认搜索限制")
    batch_size: int = Field(default=100, description="批处理大小")
    
    # ============================================================================
    # 缓存配置 / Cache Configuration
    # ============================================================================
    cache_ttl: int = Field(default=3600, description="缓存生存时间（秒）")
    enable_caching: bool = Field(default=True, description="启用缓存")
    
    # ============================================================================
    # 速率限制配置 / Rate Limiting Configuration
    # ============================================================================
    api_rate_limit: int = Field(default=100, description="API速率限制（每分钟请求数）")
    rate_limit_window: int = Field(default=60, description="速率限制窗口（秒）")
    
    # ============================================================================
    # 日志配置 / Logging Configuration
    # ============================================================================
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # ============================================================================
    # 搜索索引配置 / Search Index Configuration
    # ============================================================================
    bm25_index_path: str = Field(default="data/bm25_index.pkl", description="BM25索引文件路径")
    faiss_index_path: str = Field(default="data/game_embeddings.faiss", description="Faiss索引文件路径")
    game_id_mapping_path: str = Field(default="data/game_id_mapping.json", description="游戏ID映射文件路径")
    
    # BM25搜索参数 / BM25 Search Parameters
    bm25_k1: float = Field(default=1.5, description="BM25 k1参数")
    bm25_b: float = Field(default=0.75, description="BM25 b参数")
    
    # 语义搜索参数 / Semantic Search Parameters
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="嵌入模型名称")
    semantic_search_top_k: int = Field(default=100, description="语义搜索top-k结果数")
    
    # 融合排序参数 / Fusion Ranking Parameters
    bm25_weight: float = Field(default=0.6, description="BM25权重")
    semantic_weight: float = Field(default=0.4, description="语义搜索权重")
    
    # ============================================================================
    # 安全和限制配置 / Security and Rate Limiting Configuration
    # ============================================================================
    rate_limit_requests: int = Field(default=100, description="每分钟请求限制")
    rate_limit_window: int = Field(default=60, description="限制窗口时间（秒）")
    max_query_length: int = Field(default=200, description="最大查询长度")
    enable_security_validation: bool = Field(default=True, description="启用安全验证")

    # ============================================================================
    # 功能开关 / Feature Flags
    # ============================================================================
    enable_semantic_search: bool = Field(default=True, description="启用语义搜索")
    enable_bm25_search: bool = Field(default=True, description="启用BM25搜索")
    enable_fusion_ranking: bool = Field(default=True, description="启用融合排序")
    enable_search_suggestions: bool = Field(default=True, description="启用搜索建议")
    enable_analytics: bool = Field(default=False, description="启用分析")
    
    class Config:
        """Pydantic配置类"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局设置实例 / Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取应用程序设置的单例实例
    Get singleton instance of application settings.
    
    Returns:
        Settings: 配置设置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    重新加载设置（主要用于测试）
    Reload settings (mainly for testing).
    
    Returns:
        Settings: 新的配置设置实例
    """
    global _settings
    _settings = Settings()
    return _settings
