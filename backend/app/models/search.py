"""
Search Models

This module defines Pydantic models for search functionality, including
search requests, filters, sorting options, and response structures.

Phase 1 (Current): Basic text search with filters
Phase 2 (Future): Multi-field search with weighting
Phase 3 (Future): BM25 ranking algorithm
Phase 4 (Future): Semantic search with embeddings
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SortBy(str, Enum):
    """
    Sorting options for search results
    
    RELEVANCE: Sort by search relevance (default)
    PRICE_ASC: Sort by price low to high
    PRICE_DESC: Sort by price high to low
    REVIEWS: Sort by number of reviews (most reviewed first)
    NEWEST: Sort by release date (newest first)
    OLDEST: Sort by release date (oldest first)
    NAME: Sort alphabetically by name
    """
    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    REVIEWS = "reviews"
    NEWEST = "newest"
    OLDEST = "oldest"
    NAME = "name"


class SearchFilters(BaseModel):
    """
    Search filters for refining results
    
    All filters are optional and can be combined.
    Multiple genre/category filters use AND logic (must have all).
    
    TODO Phase 2: Add more filter types (platform, deck_compatible, etc.)
    """
    
    # Price filters (in cents for precision)
    price_min: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum price in cents (e.g., 999 = $9.99)"
    )
    price_max: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum price in cents (e.g., 5999 = $59.99)"
    )
    
    # Genre filters (JSONB array containment)
    genres: Optional[List[str]] = Field(
        None,
        max_items=5,
        description="Filter by genres (e.g., ['Action', 'RPG']). Must have ALL selected genres."
    )
    
    # Category filters (JSONB array containment)
    categories: Optional[List[str]] = Field(
        None,
        max_items=5,
        description="Filter by categories (e.g., ['Single-player', 'Multi-player'])"
    )
    
    # Type filter (indexed field - very fast)
    type: Optional[str] = Field(
        None,
        description="Filter by type (e.g., 'game', 'dlc', 'demo')"
    )
    
    # Date filters
    release_date_after: Optional[str] = Field(
        None,
        description="Filter games released after this date (YYYY-MM-DD)"
    )
    release_date_before: Optional[str] = Field(
        None,
        description="Filter games released before this date (YYYY-MM-DD)"
    )
    
    # Review filters
    min_reviews: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum number of reviews (for popularity filtering)"
    )
    
    # TODO Phase 2: Add more filters
    # platform: Optional[List[str]] = None  # ['Windows', 'Mac', 'Linux']
    # deck_compatible: Optional[bool] = None
    # has_dlc: Optional[bool] = None


class SearchRequest(BaseModel):
    """
    Search request model
    
    Combines text query, filters, sorting, and pagination.
    All fields except query are optional.
    
    Examples:
    - Simple search: {"query": "strategy"}
    - With filters: {"query": "RPG", "filters": {"price_max": 2000, "genres": ["RPG"]}}
    - Browse all: {"query": "", "sort_by": "reviews"}
    """
    
    query: str = Field(
        "",
        min_length=0,
        max_length=200,
        description="Search query text. Empty string returns all games (with filters)."
    )
    
    filters: Optional[SearchFilters] = Field(
        None,
        description="Optional filters to refine results"
    )
    
    sort_by: SortBy = Field(
        SortBy.RELEVANCE,
        description="Sort order for results"
    )
    
    offset: int = Field(
        0,
        ge=0,
        description="Pagination offset (starting position)"
    )
    
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Number of results per page (max 100)"
    )


class SearchResultItem(BaseModel):
    """
    Single search result item
    
    Extends game information with search-specific fields like relevance score.
    
    TODO Phase 2: Add highlighted snippets
    TODO Phase 3: Add BM25 score breakdown
    """
    
    # Game identification
    game_id: int = Field(..., description="Steam App ID")
    title: str = Field(..., description="Game title")
    
    # Basic information
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in USD")
    
    # Classification
    genres: List[str] = Field(default_factory=list, description="Game genres")
    categories: List[str] = Field(default_factory=list, description="Game categories")
    type: Optional[str] = Field(None, description="Type (game, dlc, etc.)")
    
    # Metadata
    release_date: Optional[str] = Field(None, description="Release date (YYYY-MM-DD)")
    total_reviews: Optional[int] = Field(None, description="Number of reviews")
    
    # Search relevance (Phase 1: simple score, Phase 3: BM25 score)
    relevance_score: float = Field(
        0.0,
        ge=0,
        le=1,
        description="Search relevance score (0-1, higher is more relevant)"
    )
    
    # TODO Phase 2: Add highlighted snippets
    # highlighted_text: Optional[str] = None
    
    # TODO Phase 3: Add detailed scoring
    # bm25_score: Optional[float] = None
    # semantic_score: Optional[float] = None


class SearchResponse(BaseModel):
    """
    Search response model
    
    Contains results array, pagination info, and search metadata.
    Follows the same structure as GameListResponse for consistency.
    """
    
    results: List[SearchResultItem] = Field(
        ...,
        description="Array of search results"
    )
    
    total: int = Field(
        ...,
        ge=0,
        description="Total number of matching games"
    )
    
    offset: int = Field(
        ...,
        ge=0,
        description="Current pagination offset"
    )
    
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Results per page"
    )
    
    query: str = Field(
        ...,
        description="Original search query"
    )
    
    filters_applied: Optional[SearchFilters] = Field(
        None,
        description="Filters that were applied to this search"
    )
    
    sort_by: SortBy = Field(
        ...,
        description="Sort order used"
    )
    
    # TODO Phase 2: Add search timing
    # search_time_ms: Optional[float] = None


# Export all models
__all__ = [
    'SortBy',
    'SearchFilters',
    'SearchRequest',
    'SearchResultItem',
    'SearchResponse',
]

