"""
Search Service

This module implements the search logic for finding games based on
text queries and filters. It handles database queries, filtering,
sorting, and result transformation.

Implementation Phases:
- Phase 1 (Complete): Basic ILIKE search on name field with filters
- Phase 2 (Complete): Multi-field search with weighting
- Phase 3 (Complete): BM25 ranking algorithm
- Phase 4 (Complete): Semantic search with pgvector
"""

from typing import Dict, Any, Optional, List
from supabase import Client
import logging
from app.config import settings
from app.models.search import SearchFilters, SortBy
from rank_bm25 import BM25Okapi
from app.services.embedding_service import EmbeddingService
from fastapi import HTTPException
import re
import numpy as np
import json

logger = logging.getLogger(__name__)


class SearchService:
    """
    Search service for finding and filtering games
    
    This service handles:
    - Text search in game names (Phase 1) and descriptions (Phase 2+)
    - BM25 ranking for relevance scoring (Phase 3)
    - Filtering by price, genre, category, type, date, reviews
    - Sorting by relevance, price, reviews, date, name
    - Pagination of results
    
    Phase 3: BM25 ranking algorithm integrated
    TODO Phase 4: Add semantic search with embeddings
    """
    
    def __init__(self, db_client: Client):
        """
        Initialize search service with database client
        
        Args:
            db_client: Supabase client instance
        """
        self.db = db_client
        self._bm25_cache = {}  # Cache for BM25 models
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25 processing
        
        Converts text to lowercase and splits on non-alphanumeric characters.
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of tokens
        """
        if not text:
            return []
        # Convert to lowercase and split on non-alphanumeric characters
        tokens = re.findall(r'\w+', text.lower())
        return tokens
    
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
                # Multiple .contains() calls create AND logic (must have all genres)
                if filters.genres:
                    import json
                    for genre in filters.genres:
                        # Convert to JSON string format
                        query_builder = query_builder.contains('genres', json.dumps([genre]))
                    logger.debug(f"Applied filter: genres contains ALL of {filters.genres} (AND logic)")
                
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
                # Phase 3: BM25 sorting is done in post-processing
                # Don't apply database-level sorting for relevance
                # BM25 scores will be calculated and sorted after query
                if not query.strip():
                    # No query = no relevance, sort by name as fallback
                    query_builder = query_builder.order('name', desc=False)
                    logger.debug("Applied sort: name ASC (no query, fallback)")
                else:
                    # With query: fetch results without sorting, will sort by BM25 later
                    logger.debug("Skipping database sort - will sort by BM25 score in post-processing")
            
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
            # Phase 3: Calculate BM25 scores for all results together (batch)
            bm25_scores = self._calculate_bm25_scores_batch(result.data, query)
            
            results = []
            for i, game in enumerate(result.data):
                # Keep v2 score for comparison/fallback
                simple_score = self._calculate_relevance_score_v2(game, query)
                
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
                    'relevance_score': simple_score,  # Keep for backward compatibility
                    'bm25_score': bm25_scores[i]  # BM25 score from batch calculation
                })
            
            # ===================================================================
            # POST-PROCESSING: Sort by BM25 score if relevance sort
            # ===================================================================
            if sort_by == SortBy.RELEVANCE and query.strip():
                # Sort results by BM25 score (descending)
                results.sort(key=lambda x: x['bm25_score'], reverse=True)
                logger.debug(f"Sorted {len(results)} results by BM25 score")
            
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
    
    def _calculate_bm25_scores_batch(self, games: List[Dict[str, Any]], query: str) -> List[float]:
        """
        Calculate BM25 relevance scores for a batch of games (Phase 3)
        
        BM25 (Best Matching 25) is a probabilistic ranking function used in
        information retrieval. This batch implementation calculates scores
        across all documents together for better IDF (inverse document frequency).
        
        This implementation:
        - Tokenizes query and all document texts
        - Creates BM25 corpus from all documents
        - Calculates BM25 score for name field (weight: 2.0)
        - Calculates BM25 score for description field (weight: 1.0)
        - Combines scores with field weighting
        
        Args:
            games: List of game data dictionaries
            query: Search query
        
        Returns:
            List of BM25 relevance scores (higher is more relevant)
        """
        if not query.strip() or not games:
            return [0.0] * len(games)
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return [0.0] * len(games)
        
        scores = []
        
        # ===================================================================
        # NAME FIELD (Weight: 2.0 - highest priority)
        # ===================================================================
        # Build corpus of all game names
        name_corpus = []
        for game in games:
            name = game.get('name', '')
            name_tokens = self._tokenize(name) if name else []
            name_corpus.append(name_tokens if name_tokens else [''])
        
        # Create BM25 model for all names
        if name_corpus:
            bm25_names = BM25Okapi(name_corpus)
            name_scores = bm25_names.get_scores(query_tokens)
        else:
            name_scores = [0.0] * len(games)
        
        # ===================================================================
        # DESCRIPTION FIELD (Weight: 1.0)
        # ===================================================================
        # Build corpus of all descriptions
        desc_corpus = []
        for game in games:
            description = game.get('short_description', '')
            desc_tokens = self._tokenize(description) if description else []
            desc_corpus.append(desc_tokens if desc_tokens else [''])
        
        # Create BM25 model for all descriptions
        if desc_corpus:
            bm25_descs = BM25Okapi(desc_corpus)
            desc_scores = bm25_descs.get_scores(query_tokens)
        else:
            desc_scores = [0.0] * len(games)
        
        # ===================================================================
        # COMBINE SCORES
        # ===================================================================
        for i in range(len(games)):
            total_score = (name_scores[i] * 2.0) + (desc_scores[i] * 1.0)
            scores.append(round(total_score, 4))
        
        return scores
    
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
    
    # ========================================================================
    # PHASE 4: Semantic Search with pgvector
    # ========================================================================
    
    async def semantic_search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 20,
        offset: int = 0,
        min_similarity: float = 0.0
    ) -> Dict[str, Any]:
        """
        Semantic search using pgvector embeddings
        
        This method uses vector similarity (cosine similarity) to find
        games that are semantically similar to the query, even if they
        don't contain the exact words.
        
        Args:
            query: Search query text
            filters: Optional filters (price, genres, type, etc.)
            limit: Number of results to return
            offset: Pagination offset
            min_similarity: Minimum similarity threshold (0.0-1.0)
        
        Returns:
            Dictionary with results and metadata
        
        Example:
            results = await search_service.semantic_search(
                query="space exploration game",
                filters=SearchFilters(price_max=5000),
                limit=20
            )
        """
        logger.info(f"Semantic search: query='{query}', limit={limit}")
        
        try:
            # Generate query embedding
            query_embedding = EmbeddingService.encode_query(query)
            logger.debug(f"Generated query embedding (dim: {len(query_embedding)})")
            
            # Build RPC parameters
            params = {
                'query_embedding': query_embedding,
                'match_limit': limit,
                'match_offset': offset,
                'min_similarity': min_similarity
            }
            
            # Add filters if provided
            if filters:
                if filters.price_max:
                    params['price_max'] = filters.price_max
                if filters.genres:
                    params['genres_filter'] = filters.genres
                if filters.type:
                    params['type_filter'] = filters.type
            
            # Call PostgreSQL function with schema prefix
            # IMPORTANT: Use schema() to specify the correct schema (steam, not public)
            logger.debug(f"Calling steam.search_games_semantic with params: {list(params.keys())}")
            try:
                result = self.db.schema(settings.DATABASE_SCHEMA).rpc('search_games_semantic', params).execute()
            except Exception as e:
                # If function doesn't exist, use Python-side semantic search as fallback
                error_msg = str(e)
                if 'Could not find the function' in error_msg or 'PGRST202' in error_msg:
                    logger.warning("⚠️  PostgreSQL function 'steam.search_games_semantic' not found!")
                    logger.warning("   Using Python-side semantic search fallback.")
                    logger.warning("   For better performance, create the function in Supabase SQL Editor.")
                    logger.warning("   See: CREATE_FUNCTIONS_IN_SUPABASE.md")
                    
                    # Use Python-side semantic search
                    return await self._python_semantic_search(query, filters, limit, offset, min_similarity)
                raise
            
            if not result.data:
                logger.info("No semantic search results found")
                return {
                    'results': [],
                    'total': 0,
                    'offset': offset,
                    'limit': limit,
                    'query': query,
                    'search_type': 'semantic',
                    'sort_by': SortBy.RELEVANCE,  # Semantic search always sorts by similarity
                    'filters_applied': filters.dict() if filters else None
                }
            
            # Transform results
            results = []
            for game in result.data:
                results.append({
                    'game_id': game['appid'],
                    'title': game['name'],
                    'description': game.get('short_description', ''),
                    'price': round(game['price_cents'] / 100, 2) if game['price_cents'] else 0.0,
                    'genres': game.get('genres', []),
                    'categories': game.get('categories', []),
                    'type': game.get('type'),
                    'release_date': game.get('release_date'),
                    'total_reviews': game.get('total_reviews'),
                    'similarity_score': round(game['similarity'], 4),
                    'relevance_score': round(game['similarity'], 4)  # For compatibility
                })
            
            logger.info(f"✓ Semantic search returned {len(results)} results")
            
            return {
                'results': results,
                'total': len(results),  # TODO: Get actual total count
                'offset': offset,
                'limit': limit,
                'query': query,
                'search_type': 'semantic',
                'sort_by': SortBy.RELEVANCE,  # Semantic search always sorts by similarity
                'filters_applied': filters.dict() if filters else None
            }
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}", exc_info=True)
            raise
    
    async def hybrid_search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        limit: int = 20,
        offset: int = 0,
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        Hybrid search combining BM25 and semantic search
        
        Uses Reciprocal Rank Fusion (RRF) to combine results from:
        - BM25 lexical matching (keyword-based)
        - Vector semantic similarity (meaning-based)
        
        Args:
            query: Search query text
            filters: Optional filters
            sort_by: Sort method (only RELEVANCE uses hybrid)
            limit: Number of results to return
            offset: Pagination offset
            alpha: Fusion weight (0.0=pure semantic, 1.0=pure BM25, 0.5=balanced)
        
        Returns:
            Dictionary with fused results and metadata
        
        Example:
            results = await search_service.hybrid_search(
                query="action shooter",
                alpha=0.5,  # 50% BM25 + 50% semantic
                limit=20
            )
        """
        logger.info(f"Hybrid search: query='{query}', alpha={alpha}")
        
        # For non-relevance sorts or empty query, fall back to regular search
        if sort_by != SortBy.RELEVANCE or not query.strip():
            logger.debug("Falling back to regular search (non-relevance sort or empty query)")
            return await self.search(query, filters, sort_by, offset, limit)
        
        try:
            # Fetch more results for fusion (to improve quality)
            fetch_limit = min(200, limit * 10)
            
            # 1. BM25 Search
            logger.debug(f"Running BM25 search (limit: {fetch_limit})")
            bm25_results = await self.search(
                query, filters, SortBy.RELEVANCE, 0, fetch_limit
            )
            
            # 2. Semantic Search (with fallback handling)
            logger.debug(f"Running semantic search (limit: {fetch_limit})")
            try:
                semantic_results = await self.semantic_search(
                    query, filters, fetch_limit, 0
                )
                # Check if semantic search fell back to BM25
                if semantic_results.get('search_type') == 'semantic_fallback_bm25':
                    logger.warning("Semantic search unavailable, using BM25-only hybrid search")
                    # If semantic search fell back, just return BM25 results
                    return {
                        'results': bm25_results['results'][:limit],
                        'total': bm25_results['total'],
                        'offset': offset,
                        'limit': limit,
                        'query': query,
                        'search_type': 'hybrid_fallback_bm25',
                        'sort_by': sort_by,
                        'alpha': alpha,
                        'fallback_reason': 'Semantic search function not available',
                        'filters_applied': filters.dict() if filters else None
                    }
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
                logger.warning("Falling back to BM25-only hybrid search")
                # Return BM25 results only
                return {
                    'results': bm25_results['results'][:limit],
                    'total': bm25_results['total'],
                    'offset': offset,
                    'limit': limit,
                    'query': query,
                    'search_type': 'hybrid_fallback_bm25',
                    'sort_by': sort_by,
                    'alpha': alpha,
                    'fallback_reason': f'Semantic search error: {str(e)}',
                    'filters_applied': filters.dict() if filters else None
                }
            
            # 3. Reciprocal Rank Fusion
            logger.debug("Performing reciprocal rank fusion")
            fused_results = self._reciprocal_rank_fusion(
                bm25_results['results'],
                semantic_results['results'],
                alpha
            )
            
            # 4. Apply pagination
            paginated = fused_results[offset:offset + limit]
            
            logger.info(f"✓ Hybrid search returned {len(paginated)} results (from {len(fused_results)} fused)")
            
            return {
                'results': paginated,
                'total': len(fused_results),
                'offset': offset,
                'limit': limit,
                'query': query,
                'search_type': 'hybrid',
                'sort_by': sort_by,  # Use the provided sort_by parameter
                'alpha': alpha,
                'filters_applied': filters.dict() if filters else None
            }
            
        except Exception as e:
            logger.error(f"❌ Hybrid search failed: {e}", exc_info=True)
            raise
    
    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Dict],
        semantic_results: List[Dict],
        alpha: float,
        k: int = 60
    ) -> List[Dict]:
        """
        Reciprocal Rank Fusion for hybrid search
        
        RRF is a simple but effective method for combining ranked lists.
        It doesn't require score normalization and is robust to score scale differences.
        
        Formula:
            RRF_score(d) = 1 / (k + rank(d))
            Final_score(d) = alpha * RRF_bm25(d) + (1-alpha) * RRF_semantic(d)
        
        Args:
            bm25_results: Results from BM25 search
            semantic_results: Results from semantic search
            alpha: Weight for BM25 (0.0-1.0)
            k: Constant to prevent division by zero (default: 60)
        
        Returns:
            List of results sorted by fused score
        """
        scores = {}
        game_data = {}
        
        # BM25 scores (keyword matching)
        for rank, result in enumerate(bm25_results, start=1):
            game_id = result['game_id']
            rrf_score = 1.0 / (k + rank)
            scores[game_id] = alpha * rrf_score
            game_data[game_id] = result
        
        # Semantic scores (meaning matching)
        for rank, result in enumerate(semantic_results, start=1):
            game_id = result['game_id']
            rrf_score = 1.0 / (k + rank)
            
            if game_id in scores:
                scores[game_id] += (1 - alpha) * rrf_score
            else:
                scores[game_id] = (1 - alpha) * rrf_score
                game_data[game_id] = result
        
        # Sort by fused score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Build result list with fusion scores
        results = []
        for game_id in sorted_ids:
            result = game_data[game_id].copy()
            result['fusion_score'] = round(scores[game_id], 6)
            result['relevance_score'] = round(scores[game_id], 6)  # For compatibility
            results.append(result)
        
        return results
    
    async def _python_semantic_search(
        self,
        query: str,
        filters: Optional[SearchFilters],
        limit: int,
        offset: int,
        min_similarity: float
    ) -> Dict[str, Any]:
        """
        Python-side semantic search fallback (when PostgreSQL function unavailable)
        
        This method performs semantic search entirely in Python by:
        1. Fetching games with embeddings from database
        2. Calculating cosine similarity in Python
        3. Filtering and sorting results
        
        This is slower than PostgreSQL function but works without setup.
        """
        logger.info("Using Python-side semantic search (PostgreSQL function unavailable)")
        
        try:
            # Generate query embedding
            query_embedding = EmbeddingService.encode_query(query)
            query_vec = np.array(query_embedding)
            
            # Build database query
            query_builder = self.db.schema(settings.DATABASE_SCHEMA)\
                .table(settings.DATABASE_TABLE)\
                .select('appid,name,short_description,price_cents,genres,categories,type,release_date,total_reviews,embedding')\
                .not_.is_('embedding', 'null')\
                .limit(min(500, limit * 10))  # Fetch more for filtering
            
            # Apply filters (database-level for efficiency)
            if filters:
                if filters.price_max:
                    query_builder = query_builder.lte('price_cents', filters.price_max)
                if filters.type:
                    query_builder = query_builder.eq('type', filters.type)
                # Apply genre filter at database level (AND logic: must have ALL selected genres)
                if filters.genres:
                    import json
                    for genre in filters.genres:
                        # Convert to JSON string format for JSONB containment
                        query_builder = query_builder.contains('genres', json.dumps([genre]))
                    logger.debug(f"Applied genre filter at database level: genres contains ALL of {filters.genres}")
            
            # Execute query
            result = query_builder.execute()
            
            if not result.data:
                return {
                    'results': [],
                    'total': 0,
                    'offset': offset,
                    'limit': limit,
                    'query': query,
                    'search_type': 'semantic_python_fallback',
                    'sort_by': SortBy.RELEVANCE,
                    'filters_applied': filters.dict() if filters else None
                }
            
            # Calculate similarities
            similarities = []
            for game in result.data:
                # Parse embedding (could be string or list)
                game_embedding = game.get('embedding')
                if not game_embedding:
                    continue
                
                # Convert to numpy array
                if isinstance(game_embedding, str):
                    # Parse string format: "[0.1, 0.2, ...]"
                    try:
                        game_vec = np.array(json.loads(game_embedding))
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        logger.debug(f"Failed to parse embedding for game {game.get('appid')}: {e}")
                        continue
                elif isinstance(game_embedding, list):
                    game_vec = np.array(game_embedding)
                else:
                    logger.debug(f"Unexpected embedding type for game {game.get('appid')}: {type(game_embedding)}")
                    continue
                
                # Calculate cosine similarity
                similarity = np.dot(query_vec, game_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(game_vec))
                
                # Apply minimum similarity threshold
                if similarity < min_similarity:
                    continue
                
                # Genre filter is already applied at database level (AND logic)
                # No need to filter again here, but verify for safety
                if filters and filters.genres:
                    game_genres = game.get('genres', [])
                    # AND logic: game must have ALL selected genres
                    if not all(genre in game_genres for genre in filters.genres):
                        logger.debug(f"Game {game.get('appid')} filtered out: missing required genres")
                        continue
                
                similarities.append({
                    'game': game,
                    'similarity': float(similarity)
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Apply pagination
            paginated = similarities[offset:offset + limit]
            
            # Transform results
            results = []
            for item in paginated:
                game = item['game']
                results.append({
                    'game_id': game['appid'],
                    'title': game['name'],
                    'description': game.get('short_description', ''),
                    'price': round(game['price_cents'] / 100, 2) if game['price_cents'] else 0.0,
                    'genres': game.get('genres', []),
                    'categories': game.get('categories', []),
                    'type': game.get('type'),
                    'release_date': game.get('release_date'),
                    'total_reviews': game.get('total_reviews'),
                    'similarity_score': round(item['similarity'], 4),
                    'relevance_score': round(item['similarity'], 4)
                })
            
            logger.info(f"✓ Python semantic search returned {len(results)} results")
            
            return {
                'results': results,
                'total': len(similarities),
                'offset': offset,
                'limit': limit,
                'query': query,
                'search_type': 'semantic_python_fallback',
                'sort_by': SortBy.RELEVANCE,  # Semantic search always sorts by similarity
                'filters_applied': filters.dict() if filters else None
            }
            
        except Exception as e:
            logger.error(f"Python semantic search failed: {e}", exc_info=True)
            # Final fallback to BM25
            logger.warning("Falling back to BM25 search")
            bm25_result = await self.search(
                query, filters, SortBy.RELEVANCE, offset, limit
            )
            bm25_result['search_type'] = 'semantic_fallback_bm25'
            bm25_result['fallback_reason'] = f'Python semantic search error: {str(e)}'
            return bm25_result


# Export service
__all__ = ['SearchService']

