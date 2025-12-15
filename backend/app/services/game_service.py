"""
Game Service Module

This module contains business logic for game data retrieval and processing.
It handles:
- Fetching games from database with pagination
- Data transformation (database format → API format)
- Field mapping and price conversion

Key Transformations:
- price_cents (int) → price (float, USD): Divide by 100
- appid → game_id: Field renaming
- name → title: Field renaming
- detailed_desc → detailed_description: Field renaming

TODO: Add caching for frequently accessed games
TODO: Add support for batch game retrieval
TODO: Implement game search functionality (Phase 2)
"""

from typing import Dict, Any, List, Optional
from supabase import Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GameService:
    """
    Game service for data retrieval and processing
    
    This class handles all game-related business logic, including fetching
    games from the database, transforming data formats, and applying
    business rules.
    
    Attributes:
        db (Client): Supabase database client
    """
    
    def __init__(self, db_client: Client):
        """
        Initialize game service
        
        Args:
            db_client (Client): Connected Supabase client
        """
        self.db = db_client
    
    async def get_games_paginated(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve paginated list of games
        
        Fetches games from steam.games_prod table with pagination support.
        Transforms database fields to match API contract format.
        
        Args:
            offset (int): Starting position (default: 0)
            limit (int): Number of games to return (default: 20, max: 100)
        
        Returns:
            Dict containing:
                - games (List[Dict]): List of transformed game data
                - total (int): Total number of games in database
                - offset (int): Current offset
                - limit (int): Current limit
        
        Raises:
            Exception: If database query fails
        """
        try:
            # Enforce maximum limit
            limit = min(limit, 100)
            
            logger.info(f"Fetching games: offset={offset}, limit={limit}")
            
            # Query games from database using the steam schema
            # Select only fields needed for list view to optimize performance
            response = self.db.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select(
                    'appid, name, price_cents, genres, categories, '
                    'short_description, total_reviews, type'
                )\
                .range(offset, offset + limit - 1)\
                .execute()
            
            # Get total count of games
            # Using count='exact' to get accurate total
            count_response = self.db.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select('appid', count='exact')\
                .execute()
            
            total = count_response.count if hasattr(count_response, 'count') else 0
            
            # Transform database records to API format
            games = [self._transform_game_data(game) for game in response.data]
            
            logger.info(f"✅ Successfully fetched {len(games)} games (total: {total})")
            
            return {
                'games': games,
                'total': total,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch games: {e}")
            raise
    
    async def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed information for a specific game
        
        Fetches complete game data including detailed description and
        all metadata fields.
        
        Args:
            game_id (int): Game ID (appid)
        
        Returns:
            Dict containing complete game data, or None if not found
        
        Raises:
            Exception: If database query fails
        """
        try:
            logger.info(f"Fetching game details: game_id={game_id}")
            
            # Query all fields for the specific game using the steam schema
            response = self.db.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select('*')\
                .eq('appid', game_id)\
                .single()\
                .execute()
            
            if not response.data:
                logger.warning(f"Game not found: game_id={game_id}")
                return None
            
            # Transform to API format
            game = self._transform_game_detail(response.data)
            
            logger.info(f"✅ Successfully fetched game: {game.get('title', 'Unknown')}")
            
            return game
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch game details: {e}")
            raise
    
    def _transform_game_data(self, db_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform database record to API format for list view
        
        Performs field mapping and data type conversions:
        - appid → game_id
        - name → title
        - price_cents → price (USD)
        
        Args:
            db_record (Dict): Raw database record
        
        Returns:
            Dict: Transformed record matching API schema
        """
        return {
            'game_id': db_record.get('appid'),
            'title': db_record.get('name', ''),
            'price': self._cents_to_usd(db_record.get('price_cents', 0)),
            'genres': db_record.get('genres', []),
            'categories': db_record.get('categories', []),
            'short_description': db_record.get('short_description'),
            'total_reviews': db_record.get('total_reviews'),
            'type': db_record.get('type', 'game')
        }
    
    def _transform_game_detail(self, db_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform database record to API format for detail view
        
        Includes all available fields for complete game information.
        
        Args:
            db_record (Dict): Raw database record
        
        Returns:
            Dict: Transformed record with all fields
        """
        return {
            'game_id': db_record.get('appid'),
            'title': db_record.get('name', ''),
            'price': self._cents_to_usd(db_record.get('price_cents', 0)),
            'genres': db_record.get('genres', []),
            'categories': db_record.get('categories', []),
            'short_description': db_record.get('short_description'),
            'detailed_description': db_record.get('detailed_desc'),
            'release_date': db_record.get('release_date'),
            'total_reviews': db_record.get('total_reviews'),
            'dlc_count': db_record.get('dlc_count'),
            'type': db_record.get('type', 'game')
        }
    
    @staticmethod
    def _cents_to_usd(cents: Optional[int]) -> float:
        """
        Convert price from cents to USD
        
        Database stores prices in cents (integer), API returns USD (float).
        Example: 1999 cents → 19.99 USD
        
        Args:
            cents (int): Price in cents
        
        Returns:
            float: Price in USD (2 decimal places)
        """
        if cents is None:
            return 0.0
        return round(cents / 100.0, 2)

