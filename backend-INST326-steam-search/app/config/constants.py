"""
Steam Game Search Engine - Constants
常量定义模块

This module contains all application constants and enums.
该模块包含所有应用程序常量和枚举。
"""

from enum import Enum
from typing import List, Dict, Any


# ============================================================================
# API Constants / API常量
# ============================================================================

API_V1_PREFIX = "/api/v1"
"""API版本1前缀"""

DEFAULT_PAGE_SIZE = 20
"""默认分页大小"""

MAX_PAGE_SIZE = 100
"""最大分页大小"""

MAX_QUERY_LENGTH = 500
"""最大查询长度"""

# ============================================================================
# Search Constants / 搜索常量
# ============================================================================

MIN_SEARCH_QUERY_LENGTH = 1
"""最小搜索查询长度"""

MAX_SEARCH_RESULTS = 1000
"""最大搜索结果数"""

DEFAULT_SEARCH_TIMEOUT = 30.0
"""默认搜索超时时间（秒）"""

# BM25搜索权重 / BM25 Search Weights
BM25_TITLE_WEIGHT = 3.0
"""标题字段权重"""

BM25_GENRE_WEIGHT = 2.0
"""类型字段权重"""

BM25_DESCRIPTION_WEIGHT = 1.0
"""描述字段权重"""

# 融合排序权重 / Fusion Ranking Weights
DEFAULT_BM25_WEIGHT = 0.6
"""默认BM25权重"""

DEFAULT_SEMANTIC_WEIGHT = 0.4
"""默认语义搜索权重"""

FUSION_BM25_WEIGHT = 0.6
"""融合排序BM25权重"""

FUSION_SEMANTIC_WEIGHT = 0.4
"""融合排序语义权重"""

QUALITY_BONUS_MULTIPLIER = 0.2
"""质量加成乘数"""

# ============================================================================
# Game Constants / 游戏常量
# ============================================================================

class CoopType(str, Enum):
    """
    合作游戏类型枚举
    Cooperative game type enumeration
    """
    SINGLE_PLAYER = "Single-player"
    LOCAL_COOP = "Local Co-op"
    ONLINE_COOP = "Online Co-op"
    LOCAL_MULTIPLAYER = "Local Multiplayer"
    ONLINE_MULTIPLAYER = "Online Multiplayer"
    MMO = "MMO"


class Platform(str, Enum):
    """
    游戏平台枚举
    Game platform enumeration
    """
    WINDOWS = "Windows"
    MAC = "Mac"
    LINUX = "Linux"
    STEAM_DECK = "SteamDeck"


class ReviewStatus(str, Enum):
    """
    评价状态枚举
    Review status enumeration
    """
    OVERWHELMINGLY_POSITIVE = "Overwhelmingly Positive"
    VERY_POSITIVE = "Very Positive"
    POSITIVE = "Positive"
    MOSTLY_POSITIVE = "Mostly Positive"
    MIXED = "Mixed"
    MOSTLY_NEGATIVE = "Mostly Negative"
    NEGATIVE = "Negative"
    VERY_NEGATIVE = "Very Negative"
    OVERWHELMINGLY_NEGATIVE = "Overwhelmingly Negative"
    NO_REVIEWS = "No Reviews"


# ============================================================================
# Security Constants / 安全常量
# ============================================================================

MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
"""最大请求大小"""

RATE_LIMIT_REQUESTS = 100
"""速率限制请求数"""

RATE_LIMIT_WINDOW = 60
"""速率限制窗口（秒）"""

# 恶意模式检测 / Malicious Pattern Detection
MALICIOUS_PATTERNS = {
    'sql_injection': [
        r"(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into)",
        r"(?i)(\'\s*or\s*\'\s*=\s*\'|\'\s*or\s*1\s*=\s*1)",
        r"(?i)(exec\s*\(|execute\s*\(|sp_executesql)"
    ],
    'xss': [
        r"(?i)(<script[^>]*>|</script>|javascript:|on\w+\s*=)",
        r"(?i)(alert\s*\(|confirm\s*\(|prompt\s*\()",
        r"(?i)(<iframe|<object|<embed|<link)"
    ],
    'command_injection': [
        r"(?i)(;\s*rm\s+|;\s*cat\s+|;\s*ls\s+|;\s*pwd)",
        r"(?i)(\|\s*nc\s+|\|\s*netcat|\|\s*wget|\|\s*curl)",
        r"(?i)(&&\s*rm|&&\s*cat|&&\s*ls)"
    ]
}
"""恶意模式正则表达式"""

# ============================================================================
# Health Check Constants / 健康检查常量
# ============================================================================

class HealthStatus(str, Enum):
    """
    健康状态枚举
    Health status enumeration
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


HEALTH_CHECK_TIMEOUT = 5.0
"""健康检查超时时间（秒）"""

# ============================================================================
# Logging Constants / 日志常量
# ============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""日志格式"""

SECURITY_LOG_FORMAT = "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
"""安全日志格式"""

# ============================================================================
# Game Genres / 游戏类型
# ============================================================================

POPULAR_GENRES: List[str] = [
    "Action", "Adventure", "RPG", "Strategy", "Simulation", "Sports",
    "Racing", "Puzzle", "Platformer", "Fighting", "Shooter", "Horror",
    "Survival", "Sandbox", "MMORPG", "Battle Royale", "Roguelike",
    "Metroidvania", "Tower Defense", "Real-time Strategy", "Turn-based Strategy",
    "Visual Novel", "Dating Sim", "Educational", "Music", "Party"
]
"""流行游戏类型列表"""

# ============================================================================
# Mock Data Constants / 模拟数据常量
# ============================================================================

MOCK_GAMES_COUNT = 50
"""模拟游戏数据数量"""

SAMPLE_DEVELOPERS: List[str] = [
    "Supergiant Games", "ConcernedApe", "Team Cherry", "Re-Logic",
    "Klei Entertainment", "Motion Twin", "Dead Cells", "Hades",
    "Indie Studio", "Big Publisher", "Small Team", "Solo Developer"
]
"""示例开发者列表"""

SAMPLE_PUBLISHERS: List[str] = [
    "Steam", "Epic Games", "GOG", "Humble Bundle", "itch.io",
    "Microsoft", "Sony", "Nintendo", "Ubisoft", "EA", "Activision"
]
"""示例发行商列表"""

# ============================================================================
# Error Messages / 错误消息
# ============================================================================

ERROR_MESSAGES: Dict[str, str] = {
    "GAME_NOT_FOUND": "Game not found",
    "INVALID_QUERY": "Invalid search query",
    "SEARCH_TIMEOUT": "Search request timed out",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    "MALICIOUS_INPUT": "Potentially malicious input detected",
    "INTERNAL_ERROR": "Internal server error",
    "VALIDATION_ERROR": "Input validation failed"
}
"""错误消息常量"""
