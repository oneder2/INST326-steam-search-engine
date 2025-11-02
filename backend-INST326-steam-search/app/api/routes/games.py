"""
Steam Game Search Engine - Games API Routes
游戏API路由模块

This module contains all game-related API endpoints including game details
and game information retrieval.
该模块包含所有游戏相关的API端点，包括游戏详情和游戏信息检索。
"""

from fastapi import APIRouter, HTTPException, Path, Request, Depends
from typing import Dict, Any, Optional
import logging
import time

from ...core import get_search_engine, GameSearchEngine
from ..schemas.game import GameDetailResponse
from ..schemas.common import ErrorResponse
from ...utils.logging import log_api_request, PerformanceTimer

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)

# 创建路由器 / Create router
router = APIRouter(prefix="/games", tags=["games"])


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


@router.get("/{game_id}", response_model=GameDetailResponse, responses={
    400: {"model": ErrorResponse, "description": "Invalid game ID"},
    404: {"model": ErrorResponse, "description": "Game not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_game_detail(
    game_id: int = Path(..., gt=0, description="Steam游戏ID，必须为正整数"),
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> GameDetailResponse:
    """
    获取游戏详细信息
    Retrieve comprehensive information about a specific game using its Steam game ID.
    
    根据Steam游戏ID获取游戏的详细信息，包括基本信息、评价状态、兼容性等。
    Retrieves detailed game information by Steam game ID, including basic info, review status, compatibility, etc.
    
    Args:
        game_id: Steam游戏ID（必须为正整数）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        GameDetailResponse: 游戏详细信息响应
        
    Raises:
        HTTPException: 400 - 无效的游戏ID
        HTTPException: 404 - 游戏未找到
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("get_game_detail_api", auto_log=False) as timer:
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 获取游戏详细信息 / Get game detail
            game_info = await search_engine.get_game_detail(game_id)
            
            if not game_info:
                raise HTTPException(
                    status_code=404,
                    detail=f"Game with ID {game_id} not found"
                )
            
            # 构建详细响应 / Build detailed response
            response = GameDetailResponse(
                **game_info.to_dict(),
                # 可以在这里添加额外的详细信息 / Can add additional detailed info here
                full_description=game_info.description,  # 完整描述
                screenshots=[],  # 截图列表（模拟数据中为空）
                additional_info={
                    'last_updated': time.time(),
                    'data_source': 'mock_provider'
                }
            )
            
            logger.info(f"Game detail retrieved: ID={game_id}, title='{game_info.title}'")
            return response
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Game detail error for ID {game_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch game details"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path=f"/api/v1/games/{game_id}",
            status_code=200,  # 这里可能不准确，但用于演示
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'game_id': game_id}
        )


@router.get("/{game_id}/similar", response_model=list, responses={
    400: {"model": ErrorResponse, "description": "Invalid game ID"},
    404: {"model": ErrorResponse, "description": "Game not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_similar_games(
    game_id: int = Path(..., gt=0, description="Steam游戏ID，必须为正整数"),
    limit: int = 5,
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> list:
    """
    获取相似游戏推荐
    Get similar game recommendations based on the specified game.
    
    根据指定游戏的类型、开发者等信息推荐相似的游戏。
    Recommends similar games based on genre, developer, and other attributes of the specified game.
    
    Args:
        game_id: Steam游戏ID（必须为正整数）
        limit: 推荐游戏数量限制（默认5个）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        list: 相似游戏列表
        
    Raises:
        HTTPException: 400 - 无效的游戏ID
        HTTPException: 404 - 游戏未找到
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("get_similar_games_api"):
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 首先获取目标游戏信息 / First get target game info
            target_game = await search_engine.get_game_detail(game_id)
            
            if not target_game:
                raise HTTPException(
                    status_code=404,
                    detail=f"Game with ID {game_id} not found"
                )
            
            # 基于类型查找相似游戏 / Find similar games based on genres
            similar_games = []
            
            if target_game.genres:
                # 使用第一个类型查找相似游戏 / Use first genre to find similar games
                primary_genre = target_game.genres[0]
                genre_games = await search_engine.get_games_by_genre(primary_genre, limit * 2)
                
                # 过滤掉目标游戏本身 / Filter out the target game itself
                similar_games = [
                    game.to_dict() for game in genre_games 
                    if game.game_id != game_id
                ][:limit]
            
            # 如果没有找到足够的相似游戏，使用热门游戏补充 / If not enough similar games, supplement with popular games
            if len(similar_games) < limit:
                popular_games = await search_engine.get_popular_games(limit)
                for game in popular_games:
                    if game.game_id != game_id and len(similar_games) < limit:
                        game_dict = game.to_dict()
                        if game_dict not in similar_games:
                            similar_games.append(game_dict)
            
            logger.info(f"Similar games retrieved for ID {game_id}: count={len(similar_games)}")
            return similar_games
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Similar games error for ID {game_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get similar games"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path=f"/api/v1/games/{game_id}/similar",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'game_id': game_id, 'limit': limit}
        )


@router.get("/{game_id}/reviews", response_model=Dict[str, Any], responses={
    400: {"model": ErrorResponse, "description": "Invalid game ID"},
    404: {"model": ErrorResponse, "description": "Game not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_game_reviews(
    game_id: int = Path(..., gt=0, description="Steam游戏ID，必须为正整数"),
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> Dict[str, Any]:
    """
    获取游戏评价信息
    Get game review information and statistics.
    
    获取游戏的评价统计信息，包括评价状态、评分等。
    Retrieves game review statistics including review status and ratings.
    
    Args:
        game_id: Steam游戏ID（必须为正整数）
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        Dict[str, Any]: 游戏评价信息
        
    Raises:
        HTTPException: 400 - 无效的游戏ID
        HTTPException: 404 - 游戏未找到
        HTTPException: 500 - 内部服务器错误
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("get_game_reviews_api"):
            # 检查搜索引擎是否已初始化 / Check if search engine is initialized
            if not search_engine.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Search engine not initialized"
                )
            
            # 获取游戏信息 / Get game info
            game_info = await search_engine.get_game_detail(game_id)
            
            if not game_info:
                raise HTTPException(
                    status_code=404,
                    detail=f"Game with ID {game_id} not found"
                )
            
            # 构建评价信息响应 / Build review info response
            review_info = {
                'game_id': game_id,
                'game_title': game_info.title,
                'review_status': game_info.review_status,
                'review_summary': {
                    'overall_status': game_info.review_status,
                    'recommendation_percentage': _get_recommendation_percentage(game_info.review_status),
                    'total_reviews': _get_mock_review_count(game_info.review_status),
                    'recent_reviews': game_info.review_status
                },
                'review_breakdown': _get_review_breakdown(game_info.review_status),
                'last_updated': time.time()
            }
            
            logger.info(f"Game reviews retrieved for ID {game_id}: status='{game_info.review_status}'")
            return review_info
            
    except HTTPException:
        # 重新抛出HTTP异常 / Re-raise HTTP exceptions
        raise
    except Exception as e:
        # 记录错误并返回500 / Log error and return 500
        logger.error(f"Game reviews error for ID {game_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get game reviews"
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path=f"/api/v1/games/{game_id}/reviews",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            query_params={'game_id': game_id}
        )


def _get_recommendation_percentage(review_status: str) -> int:
    """根据评价状态获取推荐百分比 / Get recommendation percentage based on review status"""
    percentages = {
        'Overwhelmingly Positive': 95,
        'Very Positive': 85,
        'Positive': 75,
        'Mostly Positive': 65,
        'Mixed': 50,
        'Mostly Negative': 35,
        'Negative': 25,
        'Very Negative': 15,
        'No Reviews': 0
    }
    return percentages.get(review_status, 50)


def _get_mock_review_count(review_status: str) -> int:
    """根据评价状态获取模拟评价数量 / Get mock review count based on review status"""
    counts = {
        'Overwhelmingly Positive': 50000,
        'Very Positive': 25000,
        'Positive': 10000,
        'Mostly Positive': 5000,
        'Mixed': 3000,
        'Mostly Negative': 2000,
        'Negative': 1000,
        'Very Negative': 500,
        'No Reviews': 0
    }
    return counts.get(review_status, 1000)


def _get_review_breakdown(review_status: str) -> Dict[str, int]:
    """获取评价分解信息 / Get review breakdown information"""
    total_reviews = _get_mock_review_count(review_status)
    recommendation_pct = _get_recommendation_percentage(review_status)
    
    positive_reviews = int(total_reviews * recommendation_pct / 100)
    negative_reviews = total_reviews - positive_reviews
    
    return {
        'positive': positive_reviews,
        'negative': negative_reviews,
        'total': total_reviews
    }
