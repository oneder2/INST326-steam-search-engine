"""
Search Service

This module implements the search logic for finding games based on
text queries and filters. It handles database queries, filtering,
sorting, and result transformation.

Implementation Phases:
- Phase 1 (Current): Basic ILIKE search on name field with filters
- Phase 2 (Future): Multi-field search with weighting
- Phase 3 (Future): BM25 ranking algorithm
- Phase 4 (Future): Semantic search with embeddings
"""

from typing import Dict, Any, Optional, List
from supabase import Client
import logging
from app.config import settings
from app.models.search import SearchFilters, SortBy

logger = logging.getLogger(__name__)


class SearchService:
    """
    Search service for finding and filtering games
    
    This service handles:
    - Text search in game names (Phase 1) and descriptions (Phase 2+)
    - Filtering by price, genre, category, type, date, reviews
    - Sorting by relevance, price, reviews, date, name
    - Pagination of results
    
    TODO Phase 2: Add multi-field search with weighting
    TODO Phase 3: Implement BM25 ranking
    TODO Phase 4: Add semantic search with embeddings
    """
    
    def __init__(self, db_client: Client):
        """
        Initialize search service with database client
        
        Args:
            db_client: Supabase client instance
        """
        self.db = db_client
    
    async def search(
        self,
        query: str = "",
        filters: Optional[SearchFilters] = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for games with optional filters and sorting
        
        Args:
            query: Search text (searches in game name)
            filters: Optional filters (price, genre, type, etc.)
            sort_by: Sort order for results
            offset: Pagination offset
            limit: Number of results per page (max 100)
        
        Returns:
            Dictionary with:
            - results: List of matching games
            - total: Total number of matches
            - offset: Current offset
            - limit: Results per page
            - query: Original query
            
        Raises:
            Exception: If database query fails
        """
        try:
            logger.info(f"🔍 Search request: query='{query}', filters={filters}, sort={sort_by}")
            
            # Build the base query with all fields we need
            # Note: We select all fields needed for SearchResultItem
            select_fields = (
                'appid, name, short_description, price_cents, '
                'genres, categories, type, release_date, total_reviews'
            )
            
            # Start building the query
            # IMPORTANT: Use schema() to specify the correct schema (steam, not public)
            query_builder = self.db.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select(select_fields, count='exact')
            
            # ===================================================================
            # TEXT SEARCH (Phase 2: Multi-field search with OR logic)
            # ===================================================================
            if query.strip():
                # Phase 2: Search in name OR short_description
                # Supabase PostgREST uses .or() for OR conditions
                search_term = f'%{query.strip()}%'
                # Build OR query: name ILIKE query OR short_description ILIKE query
                or_condition = f'name.ilike.{search_term},short_description.ilike.{search_term}'
                query_builder = query_builder.or_(or_condition)
                logger.debug(f"Applied multi-field text search: name OR short_description ILIKE '{search_term}'")
            
            # ===================================================================
            # FILTERS
            # ===================================================================
            if filters:
                # Price filters (use indexed field for fast filtering!)
                if filters.price_min is not None:
                    query_builder = query_builder.gte('price_cents', filters.price_min)
                    logger.debug(f"Applied filter: price_cents >= {filters.price_min}")
                
                if filters.price_max is not None:
                    query_builder = query_builder.lte('price_cents', filters.price_max)
                    logger.debug(f"Applied filter: price_cents <= {filters.price_max}")
                
                # Type filter (use indexed field - very fast!)
                if filters.type:
                    query_builder = query_builder.eq('type', filters.type)
                    logger.debug(f"Applied filter: type = '{filters.type}'")
                
                # Genre filters (JSONB containment - must have ALL selected genres)
                # Uses PostgreSQL's @> operator for JSONB containment
                # Note: Supabase expects JSON string format
                if filters.genres:
                    import json
                    for genre in filters.genres:
                        # Convert to JSON string format
                        query_builder = query_builder.contains('genres', json.dumps([genre]))
                    logger.debug(f"Applied filter: genres contains {filters.genres}")
                
                # Category filters (JSONB containment)
                if filters.categories:
                    import json
                    for category in filters.categories:
                        # Convert to JSON string format
                        query_builder = query_builder.contains('categories', json.dumps([category]))
                    logger.debug(f"Applied filter: categories contains {filters.categories}")
                
                # Date filters
                if filters.release_date_after:
                    query_builder = query_builder.gte('release_date', filters.release_date_after)
                    logger.debug(f"Applied filter: release_date >= '{filters.release_date_after}'")
                
                if filters.release_date_before:
                    query_builder = query_builder.lte('release_date', filters.release_date_before)
                    logger.debug(f"Applied filter: release_date <= '{filters.release_date_before}'")
                
                # Review count filter
                if filters.min_reviews is not None:
                    query_builder = query_builder.gte('total_reviews', filters.min_reviews)
                    logger.debug(f"Applied filter: total_reviews >= {filters.min_reviews}")
            
            # ===================================================================
            # SORTING
            # ===================================================================
            # Note: For Phase 1, RELEVANCE just sorts by name
            # TODO Phase 3: Sort by BM25 score for relevance
            if sort_by == SortBy.PRICE_ASC:
                query_builder = query_builder.order('price_cents', desc=False)
                logger.debug("Applied sort: price_cents ASC")
            
            elif sort_by == SortBy.PRICE_DESC:
                query_builder = query_builder.order('price_cents', desc=True)
                logger.debug("Applied sort: price_cents DESC")
            
            elif sort_by == SortBy.REVIEWS:
                # Sort by total_reviews DESC, then by name for ties
                query_builder = query_builder.order('total_reviews', desc=True)\
                                             .order('name', desc=False)
                logger.debug("Applied sort: total_reviews DESC, name ASC")
            
            elif sort_by == SortBy.NEWEST:
                # Sort by release_date DESC (newest first), handle NULLs
                query_builder = query_builder.order('release_date', desc=True, nullsfirst=False)\
                                             .order('name', desc=False)
                logger.debug("Applied sort: release_date DESC NULLS LAST, name ASC")
            
            elif sort_by == SortBy.OLDEST:
                # Sort by release_date ASC (oldest first), handle NULLs
                query_builder = query_builder.order('release_date', desc=False, nullsfirst=False)\
                                             .order('name', desc=False)
                logger.debug("Applied sort: release_date ASC NULLS LAST, name ASC")
            
            elif sort_by == SortBy.NAME:
                # Alphabetical by name
                query_builder = query_builder.order('name', desc=False)
                logger.debug("Applied sort: name ASC")
            
            else:  # SortBy.RELEVANCE (default)
                # Phase 1: Sort by name when no better relevance available
                # TODO Phase 3: Sort by BM25 score DESC
                query_builder = query_builder.order('name', desc=False)
                logger.debug("Applied sort: name ASC (relevance placeholder)")
            
            # ===================================================================
            # PAGINATION
            # ===================================================================
            # Supabase uses range(start, end) where end is inclusive
            # So for offset=0, limit=20: range(0, 19)
            # For offset=20, limit=20: range(20, 39)
            end_index = offset + limit - 1
            query_builder = query_builder.range(offset, end_index)
            logger.debug(f"Applied pagination: range({offset}, {end_index})")
            
            # ===================================================================
            # EXECUTE QUERY
            # ===================================================================
            result = query_builder.execute()
            
            # Get total count from response
            # Supabase returns count in the response when count='exact' is used
            total = result.count if hasattr(result, 'count') and result.count is not None else 0
            
            logger.info(f"✅ Search completed: found {total} total matches, returning {len(result.data)} results")
            
            # ===================================================================
            # TRANSFORM RESULTS
            # ===================================================================
            results = []
            for game in result.data:
                # Calculate relevance score
                # Phase 2: Multi-field scoring with weights
                relevance_score = self._calculate_relevance_score_v2(game, query)
                
                # Transform to SearchResultItem format
                results.append({
                    'game_id': game['appid'],
                    'title': game['name'],
                    'description': game['short_description'],
                    'price': round(game['price_cents'] / 100, 2) if game['price_cents'] is not None else 0.0,
                    'genres': game['genres'] if game['genres'] else [],
                    'categories': game['categories'] if game['categories'] else [],
                    'type': game['type'],
                    'release_date': game['release_date'],
                    'total_reviews': game['total_reviews'],
                    'relevance_score': relevance_score
                })
            
            # Return response
            return {
                'results': results,
                'total': total,
                'offset': offset,
                'limit': limit,
                'query': query,
                'filters_applied': filters.dict() if filters else None,
                'sort_by': sort_by
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}", exc_info=True)
            raise
    
    def _calculate_relevance_score_v2(self, game: Dict[str, Any], query: str) -> float:
        """
        Calculate relevance score for a game (Phase 2: multi-field with weights)
        
        Phase 2: Multi-field matching with weights
        - Name match: weight 10 (highest priority)
        - Description match: weight 5
        - Exact match bonus
        - Starts-with bonus
        
        Args:
            game: Game data dictionary
            query: Search query
        
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not query.strip():
            return 0.5  # No query, all equally relevant
        
        total_score = 0.0
        max_possible_score = 15.0  # 10 (name) + 5 (desc)
        query_lower = query.lower()
        
        # ===================================================================
        # NAME FIELD (Weight: 10)
        # ===================================================================
        name_lower = game.get('name', '').lower()
        name_score = 0.0
        
        if query_lower in name_lower:
            # Exact match: full weight
            if query_lower == name_lower:
                name_score = 10.0
            # Starts with query: 90% weight
            elif name_lower.startswith(query_lower):
                name_score = 9.0
            # Contains query: 70% weight
            else:
                name_score = 7.0
        
        total_score += name_score
        
        # ===================================================================
        # DESCRIPTION FIELD (Weight: 5)
        # ===================================================================
        description = game.get('short_description', '')
        if description:
            desc_lower = description.lower()
            desc_score = 0.0
            
            if query_lower in desc_lower:
                # Count occurrences for better scoring
                occurrences = desc_lower.count(query_lower)
                # Starts with: 5.0, Contains once: 3.0, Multiple: up to 5.0
                if desc_lower.startswith(query_lower):
                    desc_score = 5.0
                elif occurrences > 1:
                    desc_score = min(3.0 + occurrences * 0.5, 5.0)
                else:
                    desc_score = 3.0
            
            total_score += desc_score
        
        # Normalize score to 0.0 - 1.0 range
        normalized_score = total_score / max_possible_score
        
        return round(normalized_score, 2)


# Export service
__all__ = ['SearchService']

