"""
Steam Game Search Engine - Configuration Module
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
    api_version: str = Field(default="1.0.0", description="API版本")
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
    
    # ============================================================================
    # 搜索索引配置 / Search Index Configuration
    # ============================================================================
    faiss_index_path: str = Field(default="data/game_embeddings.faiss", description="Faiss索引文件路径")
    bm25_index_path: str = Field(default="data/bm25_index.pkl", description="BM25索引文件路径")
    game_id_mapping_path: str = Field(default="data/game_id_mapping.json", description="游戏ID映射文件路径")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="嵌入模型名称")
    
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
    # 安全配置 / Security Configuration
    # ============================================================================
    secret_key: str = Field(default="your-secret-key-here", description="应用程序密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expiration: int = Field(default=3600, description="JWT过期时间（秒）")
    
    # ============================================================================
    # 外部API配置 / External API Configuration
    # ============================================================================
    steam_api_key: Optional[str] = Field(default=None, description="Steam API密钥")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    huggingface_api_key: Optional[str] = Field(default=None, description="Hugging Face API密钥")
    
    # ============================================================================
    # 监控配置 / Monitoring Configuration
    # ============================================================================
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    health_check_timeout: float = Field(default=5.0, description="健康检查超时时间")
    
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
        
    def get_database_path(self) -> str:
        """
        获取数据库文件路径
        Get the actual database file path from the URL.
        """
        if self.database_url.startswith("sqlite:///"):
            return self.database_url[10:]  # Remove 'sqlite:///' prefix
        return self.database_url
    
    def validate_paths(self) -> bool:
        """
        验证关键文件路径是否存在
        Validate that critical file paths exist.
        """
        critical_paths = [
            self.get_database_path(),
            # Note: Index files might not exist initially and will be created
        ]
        
        missing_paths = []
        for path in critical_paths:
            if not os.path.exists(path):
                missing_paths.append(path)
        
        if missing_paths:
            print(f"⚠️  Warning: Missing files: {missing_paths}")
            return False
        return True


# 全局配置实例 / Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    获取配置实例
    Get the global settings instance.
    
    Returns:
        Settings: 配置实例
    """
    return settings


def print_startup_info():
    """
    打印启动信息
    Print startup information for debugging.
    """
    print("🔧 Configuration loaded:")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug mode: {settings.debug}")
    print(f"   Database: {settings.get_database_path()}")
    print(f"   CORS origins: {len(settings.cors_origins_list)} configured")
    print(f"   Semantic search: {'✅' if settings.enable_semantic_search else '❌'}")
    print(f"   BM25 search: {'✅' if settings.enable_bm25_search else '❌'}")
    print(f"   Fusion ranking: {'✅' if settings.enable_fusion_ranking else '❌'}")
