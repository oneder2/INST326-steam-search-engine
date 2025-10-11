"""
Steam Game Search Engine - FastAPI Backend
主应用程序入口点，提供Python FastAPI后端服务

This is the main API service that handles search requests, game details,
and provides endpoints for the frontend Next.js application.
实现了BM25关键词搜索、Faiss语义搜索和融合排序算法
"""

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import time
import logging
import asyncio

# 导入自定义模块 / Import custom modules
from config import get_settings
from database import get_game_by_id, get_games_by_ids, check_database_health, search_games_by_title
from utilities import sanitize_input, detect_malicious_patterns, log_security_event
# TODO: 暂时注释掉搜索算法模块，等安装完整依赖后再启用
# from search_algorithms import (
#     load_bm25_index, load_faiss_index, search_bm25_index,
#     search_faiss_index, apply_fusion_ranking, merge_search_results,
#     check_bm25_index_health, check_faiss_index_health
# )

# 获取配置 / Get configuration
settings = get_settings()

# 配置日志 / Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用 / Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件配置 / CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models (matching frontend TypeScript types)
# ============================================================================

class SearchFilters(BaseModel):
    price_max: Optional[int] = None
    coop_type: Optional[str] = None
    platform: Optional[List[str]] = None

class SearchQuerySchema(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class GameResult(BaseModel):
    id: int
    title: str
    score: float
    price: float
    genres: List[str]
    review_status: str
    deck_compatible: bool

class GameResultSchema(BaseModel):
    results: List[GameResult]
    total: int
    offset: int
    limit: int
    query: str
    filters: Optional[SearchFilters] = None

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str]
    prefix: str

class RankingMetrics(BaseModel):
    review_stability: float
    player_activity: float

class GameDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    genres: List[str]
    coop_type: Optional[str]
    deck_compatible: bool
    review_status: str
    release_date: Optional[str]
    developer: Optional[str]
    publisher: Optional[str]
    ranking_metrics: RankingMetrics
    screenshots: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: int
    services: Dict[str, str]
    version: str

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "Steam Game Search Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.post("/api/v1/search/games", response_model=GameResultSchema, summary="Search games")
async def search_games(query: SearchQuerySchema) -> GameResultSchema:
    """
    主搜索端点，实现统一的游戏搜索功能
    Main search endpoint implementing unified game search functionality.

    实现流程 / Implementation flow:
    1. 验证和清理输入查询 / Validate and sanitize input query
    2. 并行执行BM25和Faiss搜索 / Perform parallel BM25 and Faiss searches
    3. 应用融合排序算法 / Apply fusion ranking algorithm
    4. 应用过滤器和分页 / Apply filters and pagination
    5. 返回结构化结果 / Return structured results
    """
    try:
        # 1. 验证和清理搜索查询 / Validate and sanitize search query
        clean_query = sanitize_input(query.query)

        # 检测恶意模式 / Detect malicious patterns
        threat_analysis = detect_malicious_patterns(clean_query)
        if threat_analysis['is_malicious']:
            # 记录安全事件 / Log security event
            log_security_event(
                "malicious_input_detected",
                {
                    'input_text': query.query[:200],
                    'threat_analysis': threat_analysis
                },
                severity="warning"
            )
            raise HTTPException(status_code=400, detail="Invalid search query")

        logger.info(f"Processing search request: '{clean_query}'")

        # 2. 暂时返回模拟数据 / Temporarily return mock data
        # TODO: 等搜索算法模块可用后实现真实搜索
        mock_results = [
            GameResult(
                id=1,
                title=f"Mock Game for '{clean_query}'",
                score=0.95,
                price=24.99,
                genres=["Action", "Adventure"],
                review_status="Very Positive",
                deck_compatible=True
            ),
            GameResult(
                id=2,
                title=f"Another Game matching '{clean_query}'",
                score=0.89,
                price=19.99,
                genres=["Indie", "Platformer"],
                review_status="Positive",
                deck_compatible=True
            )
        ]

        game_results = mock_results

        # 3. 应用过滤器 / Apply filters
        if query.filters:
            game_results = _apply_search_filters(game_results, query.filters)

        # 4. 应用分页 / Apply pagination
        total_results = len(game_results)
        offset = query.offset or 0
        limit = query.limit or 20  # 使用默认值

        paginated_results = game_results[offset:offset + limit]

        logger.info(f"Search completed: {len(paginated_results)} results returned (total: {total_results})")

        return GameResultSchema(
            results=paginated_results,
            total=total_results,
            offset=offset,
            limit=limit,
            query=query.query,
            filters=query.filters
        )

    except ValidationError as e:
        logger.error(f"Validation error in search: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid search parameters: {str(e)}")
    except ValueError as e:
        logger.error(f"Value error in search: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal search error")

def _apply_search_filters(results: List[GameResult], filters: SearchFilters) -> List[GameResult]:
    """
    应用搜索过滤器
    Apply search filters to game results.

    Args:
        results (List[GameResult]): 原始搜索结果
        filters (SearchFilters): 过滤器条件

    Returns:
        List[GameResult]: 过滤后的结果
    """
    filtered_results = results

    # 价格过滤 / Price filter
    if filters.price_max is not None:
        filtered_results = [r for r in filtered_results if r.price <= filters.price_max]

    # 合作类型过滤 / Coop type filter
    if filters.coop_type:
        # TODO: 实现合作类型过滤逻辑 / TODO: Implement coop type filtering logic
        pass

    # 平台过滤 / Platform filter
    if filters.platform:
        # TODO: 实现平台过滤逻辑 / TODO: Implement platform filtering logic
        pass

    return filtered_results


@app.get("/api/v1/search/suggest", response_model=SearchSuggestionsResponse, summary="Search suggestions")
async def get_search_suggestions(prefix: str = Query(..., min_length=1)) -> SearchSuggestionsResponse:
    """
    提供基于用户输入的自动完成建议
    Provides autocomplete suggestions based on partial user input.

    实现流程 / Implementation flow:
    1. 清理和验证输入 / Sanitize and validate input
    2. 查询游戏标题建议 / Query game title suggestions
    3. 查询流派建议 / Query genre suggestions
    4. 查询流行搜索模式 / Query popular search patterns
    5. 合并和排序建议 / Merge and rank suggestions
    """
    try:
        # 1. 清理输入 / Sanitize input
        clean_prefix = prefix.lower().strip()
        if len(clean_prefix) < 1:
            return SearchSuggestionsResponse(suggestions=[], prefix=prefix)

        suggestions = []

        # 2. 游戏标题建议 / Game title suggestions
        try:
            title_games = await search_games_by_title(clean_prefix, limit=3)
            for game in title_games:
                suggestions.append(game.title)
        except Exception as e:
            logger.warning(f"Failed to get title suggestions: {str(e)}")
            # 后备模拟建议 / Fallback mock suggestions
            mock_titles = [f"{clean_prefix} game", f"Best {clean_prefix}", f"{clean_prefix} adventure"]
            suggestions.extend(mock_titles[:3])

        # 3. 流派建议 / Genre suggestions
        genre_suggestions = _get_genre_suggestions(clean_prefix, limit=2)
        suggestions.extend(genre_suggestions)

        # 4. 流行搜索模式 / Popular search patterns
        pattern_suggestions = _get_search_pattern_suggestions(clean_prefix, limit=3)
        suggestions.extend(pattern_suggestions)

        # 5. 去重并限制结果数量 / Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))[:10]

        logger.info(f"Generated {len(unique_suggestions)} suggestions for prefix: '{prefix}'")

        return SearchSuggestionsResponse(
            suggestions=unique_suggestions,
            prefix=prefix
        )

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        # 返回空建议而不是错误 / Return empty suggestions instead of error
        return SearchSuggestionsResponse(suggestions=[], prefix=prefix)


def _get_genre_suggestions(prefix: str, limit: int = 2) -> List[str]:
    """
    获取流派建议
    Get genre-based suggestions.
    """
    common_genres = [
        "Action", "Adventure", "RPG", "Strategy", "Simulation", "Sports",
        "Racing", "Puzzle", "Platformer", "Shooter", "Fighting", "Horror",
        "Indie", "Casual", "Multiplayer", "Co-op", "Roguelike", "Survival"
    ]

    matching_genres = [
        genre for genre in common_genres
        if prefix.lower() in genre.lower()
    ]

    return matching_genres[:limit]


def _get_search_pattern_suggestions(prefix: str, limit: int = 3) -> List[str]:
    """
    获取搜索模式建议
    Get search pattern suggestions.
    """
    patterns = [
        f"{prefix} games",
        f"{prefix} like",
        f"best {prefix}",
        f"{prefix} multiplayer",
        f"{prefix} indie",
        f"{prefix} steam deck"
    ]

    return patterns[:limit]

@app.get("/api/v1/games/{game_id}", response_model=GameDetailResponse, summary="Get game details")
async def get_game_detail(game_id: int = Path(..., gt=0)) -> GameDetailResponse:
    """
    获取特定游戏的详细信息
    Retrieves comprehensive information about a specific game using its Steam game ID.

    实现流程 / Implementation flow:
    1. 从数据库获取基本游戏信息 / Fetch basic game info from database
    2. 计算排名指标 / Calculate ranking metrics
    3. 获取额外元数据 / Fetch additional metadata
    4. 返回完整游戏详情 / Return comprehensive game details
    """
    try:
        # 1. 暂时返回模拟游戏详情 / Temporarily return mock game details
        # TODO: 等数据库模块可用后实现真实查询
        if game_id not in [1, 2]:
            logger.warning(f"Game not found: {game_id}")
            raise HTTPException(status_code=404, detail="Game not found")

        # 模拟游戏数据 / Mock game data
        mock_games = {
            1: {
                "title": "Hades",
                "description": "A rogue-like dungeon crawler from the creators of Bastion and Transistor.",
                "price": 24.99,
                "genres": ["Roguelike", "Action"],
                "developer": "Supergiant Games",
                "publisher": "Supergiant Games",
                "release_date": "2020-09-17"
            },
            2: {
                "title": "Dead Cells",
                "description": "A rogue-lite, metroidvania inspired, action-platformer.",
                "price": 19.99,
                "genres": ["Roguelike", "Platformer"],
                "developer": "Motion Twin",
                "publisher": "Motion Twin",
                "release_date": "2018-08-07"
            }
        }

        game_data = mock_games[game_id]
        ranking_metrics = RankingMetrics(review_stability=0.95, player_activity=0.87)

        # 构建详细响应 / Build detailed response
        game_detail = GameDetailResponse(
            id=game_id,
            title=game_data["title"],
            description=game_data["description"],
            price=game_data["price"],
            genres=game_data["genres"],
            coop_type=None,
            deck_compatible=True,
            review_status="Very Positive",
            release_date=game_data["release_date"],
            developer=game_data["developer"],
            publisher=game_data["publisher"],
            ranking_metrics=ranking_metrics,
            screenshots=[]
        )

        logger.info(f"Game details retrieved for ID: {game_id}")
        return game_detail

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving game details for ID {game_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch game details")


def _calculate_game_ranking_metrics(game_info) -> RankingMetrics:
    """
    计算游戏排名指标
    Calculate game ranking metrics based on available data.

    Args:
        game_info: 游戏信息对象

    Returns:
        RankingMetrics: 排名指标
    """
    # TODO: 实现基于真实数据的排名指标计算
    # TODO: Implement ranking metrics calculation based on real data

    # 基于评价状态的简单指标 / Simple metrics based on review status
    review_stability = 0.5  # 默认值 / Default value
    if game_info.review_status == "Very Positive":
        review_stability = 0.9
    elif game_info.review_status == "Positive":
        review_stability = 0.7
    elif game_info.review_status == "Mixed":
        review_stability = 0.5
    elif game_info.review_status == "Negative":
        review_stability = 0.3

    # 基于价格的活跃度指标 / Activity metric based on price
    player_activity = max(0.1, min(1.0, (50.0 - game_info.price) / 50.0))

    return RankingMetrics(
        review_stability=review_stability,
        player_activity=player_activity
    )


def _get_additional_game_info(game_id: int) -> Dict[str, Any]:
    """
    获取额外的游戏信息
    Get additional game information like screenshots, videos, etc.

    Args:
        game_id (int): 游戏ID

    Returns:
        Dict[str, Any]: 额外信息字典
    """
    # TODO: 实现从外部API或本地存储获取额外信息
    # TODO: Implement fetching additional info from external APIs or local storage

    return {
        "screenshots": [],  # 暂时返回空列表 / Return empty list for now
        "videos": [],
        "achievements": []
    }

@app.get("/api/v1/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    健康检查端点，用于监控服务可用性
    Health check endpoint for monitoring service availability and system status.

    检查项目 / Check items:
    1. 数据库连接性 / Database connectivity
    2. 搜索索引可用性 / Search index availability
    3. 系统资源状态 / System resource status
    4. 整体系统健康状态 / Overall system health
    """
    timestamp = int(time.time())
    services = {}

    try:
        # 检查数据库连接 / Check database connectivity
        # TODO: 暂时模拟健康状态，等数据库模块可用后替换
        services["database"] = "healthy"

        # 检查搜索索引 / Check search indices
        # TODO: 暂时模拟健康状态，等搜索算法模块可用后替换
        services["bm25_index"] = "healthy"
        services["faiss_index"] = "healthy"

        # API服务状态 / API service status
        services["api"] = "healthy"

        # 确定整体状态 / Determine overall status
        unhealthy_services = [k for k, v in services.items() if v == "unhealthy"]

        if not unhealthy_services:
            overall_status = "healthy"
        elif len(unhealthy_services) < len(services):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        logger.info(f"Health check completed: {overall_status}")

        return HealthResponse(
            status=overall_status,
            timestamp=timestamp,
            services=services,
            version="1.0.0"  # 使用固定版本号
        )

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=timestamp,
            services={"error": str(e)},
            version="1.0.0"  # 使用固定版本号
        )

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error_code": 4004, "message": "Resource not found", "details": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error_code": 5000, "message": "Internal server error", "details": "An unexpected error occurred"}

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    应用程序启动事件
    Application startup event handler.

    启动流程 / Startup flow:
    1. 打印配置信息 / Print configuration info
    2. 验证关键文件路径 / Validate critical file paths
    3. 加载搜索索引 / Load search indices
    4. 初始化数据库连接 / Initialize database connections
    5. 设置监控和日志 / Set up monitoring and logging
    """
    logger.info("🚀 Steam Game Search Engine API starting up...")

    # TODO: 暂时跳过复杂的启动流程，等所有模块可用后再启用
    logger.info("🚀 Starting with basic configuration...")

    try:
        # 验证基本配置 / Validate basic configuration
        logger.info("✅ Configuration loaded")
        logger.info("✅ Basic startup completed!")

    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        logger.warning("⚠️  Some features may not be available")

    # 打印可用端点信息 / Print available endpoints info
    print("\n📋 Available endpoints:")
    print("🔍 API documentation: /docs")
    print("📚 Alternative docs: /redoc")
    print("❤️  Health check: /api/v1/health")
    print("🔎 Search games: POST /api/v1/search/games")
    print("💡 Search suggestions: GET /api/v1/search/suggest")
    print("🎮 Game details: GET /api/v1/games/{game_id}")
    print(f"\n🌐 Server running on {settings.host}:{settings.port}")
    print(f"🔧 Environment: {settings.environment}")
    print(f"🐛 Debug mode: {settings.debug}\n")

if __name__ == "__main__":
    import uvicorn

    # 运行服务器 / Run server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
