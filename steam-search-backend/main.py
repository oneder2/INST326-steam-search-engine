"""
Steam Game Search Engine - FastAPI Backend
Main application entry point for the Python FastAPI backend.

This is the main API service that handles search requests, game details,
and provides endpoints for the frontend Next.js application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import os

# Initialize FastAPI app
app = FastAPI(
    title="Steam Game Search Engine API",
    description="Python FastAPI backend for intelligent game search with BM25 and semantic algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://steam-search-frontend.onrender.com",
        os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    ],
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
    Main search endpoint implementing unified game search functionality.
    
    This endpoint would normally:
    1. Validate and sanitize input using validate_search_query()
    2. Perform parallel BM25 and Faiss searches
    3. Apply fusion ranking algorithm
    4. Return paginated results
    
    Currently returns mock data for deployment testing.
    """
    # Mock data for deployment testing
    mock_results = [
        GameResult(
            id=1,
            title="Hades",
            score=0.95,
            price=24.99,
            genres=["Roguelike", "Action"],
            review_status="Very Positive",
            deck_compatible=True
        ),
        GameResult(
            id=2,
            title="Dead Cells",
            score=0.89,
            price=19.99,
            genres=["Roguelike", "Platformer"],
            review_status="Very Positive", 
            deck_compatible=True
        )
    ]
    
    return GameResultSchema(
        results=mock_results,
        total=len(mock_results),
        offset=query.offset or 0,
        limit=query.limit or 20,
        query=query.query,
        filters=query.filters
    )

@app.get("/api/v1/search/suggest", response_model=SearchSuggestionsResponse, summary="Search suggestions")
async def get_search_suggestions(prefix: str) -> SearchSuggestionsResponse:
    """
    Provides autocomplete suggestions based on partial user input.
    
    This endpoint would normally:
    1. Sanitize input
    2. Query game titles, genres, and popular patterns
    3. Return ranked suggestions
    
    Currently returns mock data for deployment testing.
    """
    mock_suggestions = [
        f"{prefix}like games",
        f"{prefix} indie",
        f"{prefix} multiplayer",
        f"games like {prefix}",
        f"{prefix} steam deck"
    ]
    
    return SearchSuggestionsResponse(
        suggestions=mock_suggestions[:5],
        prefix=prefix
    )

@app.get("/api/v1/games/{game_id}", response_model=GameDetailResponse, summary="Get game details")
async def get_game_detail(game_id: int) -> GameDetailResponse:
    """
    Retrieves comprehensive information about a specific game.
    
    This endpoint would normally:
    1. Query SQLite database for game info
    2. Calculate ranking metrics
    3. Fetch additional metadata
    4. Return comprehensive game details
    
    Currently returns mock data for deployment testing.
    """
    if game_id not in [1, 2]:
        raise HTTPException(status_code=404, detail="Game not found")
    
    mock_game = GameDetailResponse(
        id=game_id,
        title="Hades" if game_id == 1 else "Dead Cells",
        description="A rogue-like dungeon crawler from the creators of Bastion and Transistor.",
        price=24.99 if game_id == 1 else 19.99,
        genres=["Roguelike", "Action"] if game_id == 1 else ["Roguelike", "Platformer"],
        coop_type=None,
        deck_compatible=True,
        review_status="Very Positive",
        release_date="2020-09-17" if game_id == 1 else "2018-08-07",
        developer="Supergiant Games" if game_id == 1 else "Motion Twin",
        publisher="Supergiant Games" if game_id == 1 else "Motion Twin",
        ranking_metrics=RankingMetrics(
            review_stability=0.95,
            player_activity=0.87
        ),
        screenshots=[]
    )
    
    return mock_game

@app.get("/api/v1/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring service availability.
    
    This endpoint would normally:
    1. Check database connectivity
    2. Verify search indices are loaded
    3. Test system resources
    4. Return comprehensive health status
    
    Currently returns mock healthy status for deployment testing.
    """
    return HealthResponse(
        status="healthy",
        timestamp=int(time.time()),
        services={
            "database": "healthy",
            "bm25_index": "healthy", 
            "faiss_index": "healthy",
            "api": "healthy"
        },
        version="1.0.0"
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
    Application startup event.
    
    In a full implementation, this would:
    1. Load BM25 and Faiss indices
    2. Initialize database connections
    3. Verify data file integrity
    4. Set up logging and monitoring
    """
    print("🚀 Steam Game Search Engine API starting up...")
    print("📚 Function documentation available at /function-library")
    print("🔍 API documentation available at /docs")
    print("❤️  Health check available at /api/v1/health")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
