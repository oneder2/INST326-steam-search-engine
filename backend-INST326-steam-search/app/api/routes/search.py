"""
Steam Game Search Engine - Search API Routes
搜索API路由模块

This module contains all search-related API endpoints including game search,
search suggestions, and related functionality.
该模块包含所有搜索相关的API端点，包括游戏搜索、搜索建议和相关功能。
"""

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import List, Optional, Dict, Any
import logging
import time

from ...core import get_search_engine, GameSearchEngine
from ..schemas.search import SearchQuerySchema, GameResultSchema, SearchSuggestionsResponse
from ..schemas.common import ErrorResponse
from ...utils.logging import log_api_request, log_search_query, PerformanceTimer

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)

# 创建路由器 / Create router
router = APIRouter(prefix="/search", tags=["search"])


def get_client_info(request: Request) -> Dict[str, Optional[str]]:
    """
    获取客户端信息
    Get client information from request.
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        Dict[str, Optional[str]]: 客户端信息
    """
    return {
        'client_ip': request.client.host if request.client else None,
        'user_agent': request.headers.get('user-agent'),
        'referer': request.headers.get('referer')
    }


@router.post("/games", response_model=GameResultSchema, responses={
    400: {"model": ErrorResponse, "description": "Invalid search query"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def search_games(
    query: SearchQuerySchema,
    request: Request,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> GameResultSchema:
    """
    执行游戏搜索
    Execute comprehensive game search with filters and pagination.
    
    这个端点实现了统一的游戏搜索功能，结合BM25关键词搜索和语义向量搜索。
    This endpoint implements unified game search functionality combining BM25 keyword search and semantic vector search.
    
    Args:
        query: 搜索查询参数，包含查询字符串、过滤器和分页信息
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        GameResultSchema: 搜索结果，包含游戏列表、总数和分页信息
        
    Raises:
        HTTPException: 400 - 无效的搜索查询
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("search_games_api", auto_log=False) as timer:
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 执行搜索 / Execute search
            search_results, total_count = await search_engine.search_games(
                query=query.query,
                filters=query.filters.dict() if query.filters else None,
                limit=query.limit,
                offset=query.offset
            )
            
            # 构建响应 / Build response
            # 将SearchResult转换为GameResult格式 / Convert SearchResult to GameResult format
            formatted_results = []
            for result in search_results:
                game_result = {
                    # 游戏基本信息 / Basic game information
                    'game_id': result.game.game_id,
                    'title': result.game.title,
                    'description': result.game.description,
                    'price': result.game.price,
                    'genres': result.game.genres,
                    'coop_type': result.game.coop_type,
                    'deck_comp': result.game.deck_comp,
                    'review_status': result.game.review_status,
                    'release_date': result.game.release_date,
                    'developer': result.game.developer,
                    'publisher': result.game.publisher,

                    # 搜索相关评分 / Search-related scores
                    'relevance_score': min(result.score / 10.0, 1.0),  # 标准化到0-1
                    'bm25_score': result.score if result.search_type in ['bm25', 'fusion'] else 0.0,
                    'semantic_score': min(result.score / 10.0, 1.0) if result.search_type in ['semantic', 'fusion'] else 0.0
                }
                formatted_results.append(game_result)

            response = GameResultSchema(
                results=formatted_results,
                total=total_count,
                offset=query.offset,
                limit=query.limit,
                query=query.query,
                filters=query.filters.dict() if query.filters else {}
            )
            
            # 记录搜索查询日志 / Log search query
            if timer.duration:
                log_search_query(
                    query=query.query,
                    results_count=len(search_results),
                    duration=timer.duration,
                    filters=query.filters.dict() if query.filters else None,
                    client_ip=client_info['client_ip']
                )
            
            logger.info(f"Search completed: query='{query.query}', results={len(search_results)}")
            return response
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal search error"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="POST",
            path="/api/v1/search/games",
            status_code=200,  # 这里可能不准确，但用于演示
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'query': query.query}
        )


@router.get("/suggest", response_model=SearchSuggestionsResponse, responses={
    400: {"model": ErrorResponse, "description": "Invalid prefix"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_search_suggestions(
    prefix: str = Query(..., min_length=1, max_length=100, description="搜索前缀"),
    limit: int = Query(default=10, ge=1, le=20, description="建议数量限制"),
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> SearchSuggestionsResponse:
    """
    获取搜索建议
    Get search suggestions based on input prefix.
    
    根据用户输入的前缀提供自动完成建议，包括游戏标题、类型和开发者建议。
    Provides autocomplete suggestions based on user input prefix, including game titles, genres, and developer suggestions.
    
    Args:
        prefix: 搜索前缀字符串（1-100字符）
        limit: 返回建议的最大数量（1-20）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        SearchSuggestionsResponse: 搜索建议响应，包含建议列表和原始前缀
        
    Raises:
        HTTPException: 400 - 无效的前缀
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("search_suggestions_api"):
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 获取搜索建议 / Get search suggestions
            suggestions = await search_engine.get_search_suggestions(prefix, limit)
            
            # 构建响应 / Build response
            response = SearchSuggestionsResponse(
                suggestions=suggestions,
                prefix=prefix
            )
            
            logger.info(f"Search suggestions generated: prefix='{prefix}', count={len(suggestions)}")
            return response
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Search suggestions error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get search suggestions"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path="/api/v1/search/suggest",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'prefix': prefix, 'limit': limit}
        )


@router.get("/popular", response_model=List[Dict[str, Any]], responses={
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_popular_games(
    limit: int = Query(default=10, ge=1, le=50, description="热门游戏数量限制"),
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> List[Dict[str, Any]]:
    """
    获取热门游戏
    Get popular games based on ratings and other criteria.
    
    根据评价状态和其他标准返回热门游戏列表。
    Returns popular games list based on review status and other criteria.
    
    Args:
        limit: 返回游戏的最大数量（1-50）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        List[Dict[str, Any]]: 热门游戏列表
        
    Raises:
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("popular_games_api"):
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 获取热门游戏 / Get popular games
            popular_games = await search_engine.get_popular_games(limit)
            
            # 转换为字典格式 / Convert to dictionary format
            games_data = [game.to_dict() for game in popular_games]
            
            logger.info(f"Popular games retrieved: count={len(games_data)}")
            return games_data
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Popular games error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get popular games"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path="/api/v1/search/popular",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'limit': limit}
        )


@router.get("/genres/{genre}", response_model=List[Dict[str, Any]], responses={
    400: {"model": ErrorResponse, "description": "Invalid genre"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_games_by_genre(
    genre: str,
    limit: int = Query(default=20, ge=1, le=50, description="游戏数量限制"),
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> List[Dict[str, Any]]:
    """
    根据类型获取游戏
    Get games by specific genre.
    
    返回指定类型的游戏列表。
    Returns games list for the specified genre.
    
    Args:
        genre: 游戏类型名称
        limit: 返回游戏的最大数量（1-50）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        List[Dict[str, Any]]: 指定类型的游戏列表
        
    Raises:
        HTTPException: 400 - 无效的类型
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("games_by_genre_api"):
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 验证类型参数 / Validate genre parameter
            if not genre or len(genre.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Genre cannot be empty"
                )
            
            # 获取指定类型的游戏 / Get games by genre
            genre_games = await search_engine.get_games_by_genre(genre, limit)
            
            # 转换为字典格式 / Convert to dictionary format
            games_data = [game.to_dict() for game in genre_games]
            
            logger.info(f"Games by genre retrieved: genre='{genre}', count={len(games_data)}")
            return games_data
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Games by genre error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get games by genre"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path=f"/api/v1/search/genres/{genre}",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'genre': genre, 'limit': limit}
        )
