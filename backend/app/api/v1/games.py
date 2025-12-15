"""
Games API Endpoints

This module provides RESTful endpoints for game data retrieval.
Supports paginated game lists and individual game details.

Endpoints:
- GET /api/v1/games: Get paginated list of games
- GET /api/v1/games/{game_id}: Get detailed information for a specific game

Phase 1 (Current): Basic data retrieval with pagination
Phase 2 (Future): Search, filtering, and ranking

TODO: Add search functionality (Phase 2)
TODO: Add filtering by genre, price, etc. (Phase 2)
TODO: Add sorting options (Phase 2)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from supabase import Client
from app.database import get_db
from app.models.game import GameListResponse, GameDetail
from app.models.common import ErrorResponse
from app.services.game_service import GameService
import logging

logger = logging.getLogger(__name__)

# Create router for game endpoints
router = APIRouter()


@router.get(
    "/games",
    response_model=GameListResponse,
    summary="Get Games List",
    description="Retrieve paginated list of games from the database",
    tags=["Games"],
    responses={
        200: {"description": "Successfully retrieved games list"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_games(
    offset: int = Query(
        0,
        ge=0,
        description="Starting position for pagination (0-indexed)"
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of games to return (max: 100)"
    ),
    db: Client = Depends(get_db)
) -> GameListResponse:
    """
    Retrieve paginated list of games
    
    This endpoint returns a paginated list of games from the steam.games_prod
    table. Each game includes basic information suitable for list display.
    
    Pagination:
    - Use 'offset' to skip games (e.g., offset=20 for page 2)
    - Use 'limit' to control page size (max 100)
    - Response includes total count for calculating total pages
    
    Example Usage:
    - Page 1: /api/v1/games?offset=0&limit=20
    - Page 2: /api/v1/games?offset=20&limit=20
    - Page 3: /api/v1/games?offset=40&limit=20
    
    Args:
        offset (int): Starting position (default: 0)
        limit (int): Number of games per page (default: 20, max: 100)
        db (Client): Injected database client
    
    Returns:
        GameListResponse: Paginated list of games with metadata
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        logger.info(f"GET /api/v1/games - offset={offset}, limit={limit}")
        
        # Create game service instance
        service = GameService(db)
        
        # Fetch paginated games
        result = await service.get_games_paginated(offset, limit)
        
        logger.info(
            f"✅ Successfully returned {len(result['games'])} games "
            f"(offset={offset}, total={result['total']})"
        )
        
        return GameListResponse(**result)
        
    except ValueError as e:
        # Handle validation errors (invalid parameters)
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"❌ Server error while fetching games: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching games"
        )


@router.get(
    "/games/{game_id}",
    response_model=GameDetail,
    summary="Get Game Details",
    description="Retrieve detailed information for a specific game",
    tags=["Games"],
    responses={
        200: {"description": "Successfully retrieved game details"},
        404: {"model": ErrorResponse, "description": "Game not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_game_detail(
    game_id: int = Path(
        ...,
        gt=0,
        description="Steam game ID (appid)"
    ),
    db: Client = Depends(get_db)
) -> GameDetail:
    """
    Retrieve detailed information for a specific game
    
    This endpoint returns complete information about a single game, including:
    - Basic information (title, price, type)
    - Descriptions (short and detailed)
    - Classifications (genres, categories)
    - Metadata (release date, reviews, DLC count)
    
    Args:
        game_id (int): Steam game ID (appid)
        db (Client): Injected database client
    
    Returns:
        GameDetail: Complete game information
        
    Raises:
        HTTPException: 404 if game not found, 500 for server errors
    """
    try:
        logger.info(f"GET /api/v1/games/{game_id}")
        
        # Create game service instance
        service = GameService(db)
        
        # Fetch game details
        game = await service.get_game_by_id(game_id)
        
        # Check if game exists
        if not game:
            logger.warning(f"⚠️ Game not found: game_id={game_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Game with ID {game_id} not found"
            )
        
        logger.info(f"✅ Successfully returned game: {game.get('title', 'Unknown')}")
        
        return GameDetail(**game)
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, etc.)
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"❌ Server error while fetching game {game_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching game details"
        )

