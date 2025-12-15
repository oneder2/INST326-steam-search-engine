"""
Game Data Models

This module contains Pydantic models for game-related data structures.
It handles the mapping between database fields (steam.games_prod) and
API response formats expected by the frontend.

Key Field Mappings (Database → API):
- appid → game_id
- name → title
- price_cents → price (converted to USD by dividing by 100)
- genres (JSONB) → genres (List[str])
- categories (JSONB) → categories (List[str])

Models:
- GameListItem: Simplified game data for list views
- GameListResponse: Paginated list of games
- GameDetail: Full game details for detail view

TODO: Add support for filtering by categories
TODO: Add support for deck compatibility detection from categories
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import date


class GameListItem(BaseModel):
    """
    Simplified game data for list views
    
    This model represents a single game in a list response with essential
    information. It maps database fields to frontend-expected format.
    
    Database Mapping:
    - appid → game_id
    - name → title
    - price_cents → price (USD)
    - genres → genres (parsed from JSONB)
    - categories → categories (parsed from JSONB)
    """
    
    game_id: int = Field(..., description="Steam game ID (appid)")
    title: str = Field(..., description="Game title")
    price: float = Field(..., ge=0, description="Game price in USD")
    genres: List[str] = Field(default_factory=list, description="Game genres")
    categories: List[str] = Field(default_factory=list, description="Game categories")
    short_description: Optional[str] = Field(None, description="Brief game description")
    total_reviews: Optional[int] = Field(None, ge=0, description="Total number of reviews")
    type: Optional[str] = Field(None, description="Item type (game, dlc, demo, etc.)")
    
    @field_validator('genres', 'categories', mode='before')
    @classmethod
    def parse_jsonb_array(cls, v: Any) -> List[str]:
        """
        Parse JSONB array fields from database
        
        Handles various input formats:
        - None → empty list
        - List → return as-is
        - String → attempt JSON parse
        
        Args:
            v: Input value (JSONB from database)
            
        Returns:
            List[str]: Parsed list of strings
        """
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except:
                return []
        return []
    
    class Config:
        json_schema_extra = {
            "example": {
                "game_id": 570,
                "title": "Dota 2",
                "price": 0.00,
                "genres": ["Action", "Free to Play", "MOBA"],
                "categories": ["Multi-player", "Co-op", "Steam Achievements"],
                "short_description": "Every day, millions of players worldwide...",
                "total_reviews": 1500000,
                "type": "game"
            }
        }


class GameListResponse(BaseModel):
    """
    Paginated game list response
    
    Contains a list of games along with pagination metadata.
    This is the standard response format for list endpoints.
    
    Attributes:
        games (List[GameListItem]): List of games for current page
        total (int): Total number of games available
        offset (int): Current offset (starting position)
        limit (int): Number of games per page
    """
    
    games: List[GameListItem] = Field(..., description="List of games")
    total: int = Field(..., ge=0, description="Total number of games")
    offset: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, le=100, description="Games per page")
    
    @property
    def has_more(self) -> bool:
        """Check if more games are available after current page"""
        return self.offset + self.limit < self.total
    
    class Config:
        json_schema_extra = {
            "example": {
                "games": [
                    {
                        "game_id": 570,
                        "title": "Dota 2",
                        "price": 0.00,
                        "genres": ["Action", "Free to Play"],
                        "categories": ["Multi-player"],
                        "short_description": "A popular MOBA game",
                        "total_reviews": 1500000,
                        "type": "game"
                    }
                ],
                "total": 50000,
                "offset": 0,
                "limit": 20
            }
        }


class GameDetail(BaseModel):
    """
    Complete game details for detail view
    
    This model contains all available information about a game,
    including extended descriptions and metadata.
    
    Database Mapping:
    - appid → game_id
    - name → title
    - price_cents → price (USD)
    - short_description → short_description
    - detailed_desc → detailed_description
    - genres/categories → parsed from JSONB
    """
    
    game_id: int = Field(..., description="Steam game ID (appid)")
    title: str = Field(..., description="Game title")
    price: float = Field(..., ge=0, description="Game price in USD")
    genres: List[str] = Field(default_factory=list, description="Game genres")
    categories: List[str] = Field(default_factory=list, description="Game categories")
    short_description: Optional[str] = Field(None, description="Brief description")
    detailed_description: Optional[str] = Field(None, description="Full description")
    release_date: Optional[date] = Field(None, description="Release date")
    total_reviews: Optional[int] = Field(None, ge=0, description="Total reviews")
    dlc_count: Optional[int] = Field(None, ge=0, description="Number of DLCs")
    type: Optional[str] = Field(None, description="Item type")
    
    @field_validator('genres', 'categories', mode='before')
    @classmethod
    def parse_jsonb_array(cls, v: Any) -> List[str]:
        """Parse JSONB array fields from database"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except:
                return []
        return []
    
    class Config:
        json_schema_extra = {
            "example": {
                "game_id": 570,
                "title": "Dota 2",
                "price": 0.00,
                "genres": ["Action", "Free to Play", "MOBA"],
                "categories": ["Multi-player", "Co-op", "Steam Achievements"],
                "short_description": "Every day, millions of players...",
                "detailed_description": "Dota 2 is a multiplayer online battle arena...",
                "release_date": "2013-07-09",
                "total_reviews": 1500000,
                "dlc_count": 0,
                "type": "game"
            }
        }

