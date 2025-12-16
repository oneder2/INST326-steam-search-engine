"""
Search API Endpoints

This module provides REST API endpoints for game search functionality.
It handles search requests with filters, sorting, and pagination.

Endpoints:
- POST /api/v1/search/games: Main search endpoint with full filter support

TODO Phase 2: Add GET /api/v1/search/suggest for search suggestions
TODO Phase 3: Add search analytics endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from app.database import get_db
from app.models.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService
import logging

logger = logging.getLogger(__name__)

# Create router for search endpoints
router = APIRouter()


@router.post(
    "/search/games",
    response_model=SearchResponse,
    summary="Search Games",
    description="Search for games with text query, filters, and sorting options",
    tags=["Search"],
    responses={
        200: {
            "description": "Successful search",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "game_id": 570,
                                "title": "Dota 2",
                                "description": "Every day, millions of players worldwide...",
                                "price": 0.0,
                                "genres": ["Action", "Strategy"],
                                "categories": ["Multi-player"],
                                "type": "game",
                                "release_date": "2013-07-09",
                                "total_reviews": 1500000,
                                "relevance_score": 0.95
                            }
                        ],
                        "total": 156,
                        "offset": 0,
                        "limit": 20,
                        "query": "strategy",
                        "filters_applied": {
                            "price_max": 2000,
                            "genres": ["Strategy"]
                        },
                        "sort_by": "reviews"
                    }
                }
            }
        },
        400: {"description": "Invalid search parameters"},
        500: {"description": "Internal server error"}
    }
)
async def search_games(
    request: SearchRequest,
    db: Client = Depends(get_db)
) -> SearchResponse:
    """
    Search for games using text query and filters
    
    **Features:**
    - Text search in game names (Phase 1) and descriptions (Phase 2+)
    - Filter by price range, genre, category, type, date, reviews
    - Sort by relevance, price, reviews, date, name
    - Pagination support
    
    **Query Examples:**
    
    1. Simple text search:
    ```json
    {
      "query": "strategy"
    }
    ```
    
    2. Search with price filter:
    ```json
    {
      "query": "RPG",
      "filters": {
        "price_max": 2000
      }
    }
    ```
    
    3. Search with multiple filters:
    ```json
    {
      "query": "action",
      "filters": {
        "price_max": 3000,
        "genres": ["Action", "Adventure"],
        "type": "game",
        "min_reviews": 100
      },
      "sort_by": "reviews",
      "offset": 0,
      "limit": 20
    }
    ```
    
    4. Browse all games (no query):
    ```json
    {
      "query": "",
      "filters": {
        "type": "game"
      },
      "sort_by": "reviews"
    }
    ```
    
    **Sort Options:**
    - `relevance`: Most relevant to search query (default)
    - `price_asc`: Price low to high
    - `price_desc`: Price high to low
    - `reviews`: Most reviewed first
    - `newest`: Newest games first
    - `oldest`: Oldest games first
    - `name`: Alphabetical by name
    
    **Filter Fields:**
    - `price_min`, `price_max`: Price range in cents
    - `genres`: Array of required genres (must have ALL)
    - `categories`: Array of required categories
    - `type`: Game type (e.g., "game", "dlc")
    - `release_date_after`, `release_date_before`: Date range
    - `min_reviews`: Minimum number of reviews
    
    Args:
        request: Search request with query, filters, sorting, and pagination
        db: Database client (injected)
    
    Returns:
        SearchResponse with results and metadata
    
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        logger.info(
            f"📥 Search request: query='{request.query}', "
            f"sort={request.sort_by}, offset={request.offset}, limit={request.limit}"
        )
        
        # Log filters if present
        if request.filters:
            logger.debug(f"Filters: {request.filters.dict(exclude_none=True)}")
        
        # Create search service and perform search
        service = SearchService(db)
        result = await service.search(
            query=request.query,
            filters=request.filters,
            sort_by=request.sort_by,
            offset=request.offset,
            limit=request.limit
        )
        
        logger.info(
            f"✅ Search successful: returned {len(result['results'])} results "
            f"out of {result['total']} total matches"
        )
        
        return result
        
    except ValueError as e:
        # Invalid parameters (e.g., negative offset, limit too high)
        logger.warning(f"⚠️ Invalid search parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search parameters: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error (database, network, etc.)
        logger.error(f"❌ Search failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed due to server error. Please try again later."
        )


# ============================================================================
# Phase 4: Semantic and Hybrid Search Endpoints
# ============================================================================

@router.post(
    "/search/semantic",
    response_model=SearchResponse,
    summary="Semantic Search",
    description="Search games using vector similarity (pgvector)",
    tags=["Search", "Semantic"]
)
async def semantic_search_endpoint(
    request: SearchRequest,
    db: Client = Depends(get_db)
) -> SearchResponse:
    """
    Semantic search using pgvector embeddings
    
    This endpoint finds games that are semantically similar to the query,
    even if they don't contain the exact words. It uses vector similarity
    (cosine similarity) to match meaning rather than keywords.
    
    **Example:**
    ```json
    {
      "query": "space exploration adventure",
      "filters": {
        "price_max": 5000
      },
      "limit": 20
    }
    ```
    
    **How it works:**
    1. Query is converted to a 384-dimensional vector embedding
    2. Database finds games with similar embeddings
    3. Results are ranked by cosine similarity
    
    **Use cases:**
    - Finding games by concept/theme
    - Discovering similar games
    - Handling typos and synonyms
    """
    try:
        logger.info(f"Semantic search request: query='{request.query}'")
        
        search_service = SearchService(db)
        result = await search_service.semantic_search(
            query=request.query,
            filters=request.filters,
            limit=request.limit or 20,
            offset=request.offset or 0
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post(
    "/search/hybrid",
    response_model=SearchResponse,
    summary="Hybrid Search",
    description="Combined BM25 and semantic search with score fusion",
    tags=["Search", "Hybrid"]
)
async def hybrid_search_endpoint(
    request: SearchRequest,
    alpha: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Fusion weight: 0.0=pure semantic, 1.0=pure BM25, 0.5=balanced"
    ),
    db: Client = Depends(get_db)
) -> SearchResponse:
    """
    Hybrid search combining BM25 and semantic search
    
    Uses Reciprocal Rank Fusion (RRF) to combine:
    - **BM25**: Keyword-based matching (exact words)
    - **Semantic**: Meaning-based matching (concepts)
    
    **Alpha Parameter:**
    - `0.0`: Pure semantic search (meaning only)
    - `0.5`: Balanced (recommended)
    - `1.0`: Pure BM25 (keywords only)
    
    **Example:**
    ```json
    {
      "query": "action shooter multiplayer",
      "filters": {
        "genres": ["Action", "Shooter"]
      },
      "limit": 20
    }
    ```
    With `alpha=0.5` (default)
    
    **Benefits:**
    - Best of both worlds
    - More robust results
    - Handles both exact matches and concepts
    
    **When to use:**
    - General search (recommended default)
    - When you want comprehensive results
    - For production search
    """
    try:
        logger.info(f"Hybrid search request: query='{request.query}', alpha={alpha}")
        
        from app.models.search import SortBy
        
        search_service = SearchService(db)
        result = await search_service.hybrid_search(
            query=request.query,
            filters=request.filters,
            sort_by=request.sort_by or SortBy.RELEVANCE,
            limit=request.limit or 20,
            offset=request.offset or 0,
            alpha=alpha
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid search failed: {str(e)}"
        )


# TODO Phase 2: Add search suggestions endpoint
# @router.get(
#     "/search/suggest",
#     summary="Get Search Suggestions",
#     description="Get autocomplete suggestions for search input",
#     tags=["Search"]
# )
# async def get_search_suggestions(
#     prefix: str,
#     limit: int = 10,
#     db: Client = Depends(get_db)
# ):
#     """
#     Get search suggestions based on input prefix
#     
#     Useful for autocomplete functionality in the frontend.
#     Returns game names, genres, and categories that match the prefix.
#     """
#     pass


# Export router
__all__ = ['router']


