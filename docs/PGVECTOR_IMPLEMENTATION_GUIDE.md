# pgvector Semantic Search Implementation Guide (Simplified)

## Why pgvector > Faiss for Supabase?

### Advantages of pgvector
✅ **Integrated with database** - No separate index files  
✅ **Automatic persistence** - Vectors stored in PostgreSQL  
✅ **SQL-based queries** - Easy to combine with filters  
✅ **Supabase native support** - Built-in extension  
✅ **Simpler architecture** - No external index management  
✅ **Incremental updates** - Add/update vectors easily  

### Comparison

| Feature | Faiss | pgvector |
|---------|-------|----------|
| Setup Complexity | High | Low |
| Storage | Separate files | Database |
| Persistence | Manual | Automatic |
| Filtering | Manual merge | SQL WHERE |
| Updates | Rebuild index | UPDATE query |
| Deployment | Extra files | Just database |
| Supabase Support | Manual | Native |

---

## Implementation Steps (Simplified)

### Step 1: Enable pgvector Extension (2 minutes)

#### 1.1 Enable in Supabase Dashboard
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

Or via Dashboard:
1. Go to Supabase Dashboard
2. Database → Extensions
3. Search "vector"
4. Enable

#### 1.2 Add Vector Column to Table
```sql
-- Add embedding column to existing games_prod table
ALTER TABLE steam.games_prod 
ADD COLUMN embedding vector(384);

-- Create index for fast similarity search
CREATE INDEX ON steam.games_prod 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Optional: Create index for other operators
-- CREATE INDEX ON steam.games_prod USING ivfflat (embedding vector_l2_ops);
```

**Note**: 384 is the dimension for `all-MiniLM-L6-v2` model. If using a different model, adjust accordingly.

---

### Step 2: Install Dependencies (5 minutes)

```bash
# Add to backend/requirements.txt
sentence-transformers==2.2.2
pgvector==0.2.4  # PostgreSQL adapter
```

**No Faiss needed!** 🎉

---

### Step 3: Create Embedding Service (30 minutes)

**File**: `backend/app/services/embedding_service.py`

```python
"""
Embedding Service for Semantic Search
Uses sentence-transformers to generate text embeddings
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generate text embeddings for semantic search using pgvector
    """
    
    # Class-level model instance (singleton pattern)
    _model: Optional[SentenceTransformer] = None
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or initialize the embedding model (singleton)"""
        if cls._model is None:
            logger.info("Loading embedding model: all-MiniLM-L6-v2")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"✓ Model loaded (dimension: {cls._model.get_sentence_embedding_dimension()})")
        return cls._model
    
    @classmethod
    def get_dimension(cls) -> int:
        """Get embedding dimension"""
        return cls.get_model().get_sentence_embedding_dimension()
    
    @classmethod
    def encode_game(cls, game: Dict[str, Any]) -> List[float]:
        """
        Create embedding for a single game
        
        Combines with weighting:
        - Game name (weight: 2x)
        - Short description (weight: 1x)
        - Genres (weight: 1x)
        
        Args:
            game: Game data dict with 'name', 'short_description', 'genres'
        
        Returns:
            List of floats (384-dimensional vector)
        """
        name = game.get('name', '')
        desc = game.get('short_description', '')
        
        # Handle genres (JSONB array)
        genres = game.get('genres', [])
        if isinstance(genres, list):
            genres_text = ' '.join(genres)
        else:
            genres_text = ''
        
        # Weighted concatenation (name appears twice for 2x weight)
        text = f"{name} {name} {desc} {genres_text}"
        
        # Generate embedding
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Convert to list for PostgreSQL
        return embedding.tolist()
    
    @classmethod
    def encode_batch(cls, games: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Batch encode multiple games (more efficient)
        
        Args:
            games: List of game data dicts
        
        Returns:
            List of embeddings (list of lists)
        """
        texts = []
        for game in games:
            name = game.get('name', '')
            desc = game.get('short_description', '')
            
            genres = game.get('genres', [])
            if isinstance(genres, list):
                genres_text = ' '.join(genres)
            else:
                genres_text = ''
            
            texts.append(f"{name} {name} {desc} {genres_text}")
        
        # Batch encode
        model = cls.get_model()
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Convert to list of lists
        return [emb.tolist() for emb in embeddings]
    
    @classmethod
    @lru_cache(maxsize=1000)
    def encode_query(cls, query: str) -> List[float]:
        """
        Encode user search query (cached for performance)
        
        Args:
            query: User search string
        
        Returns:
            List of floats (384-dimensional vector)
        """
        model = cls.get_model()
        embedding = model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
```

---

### Step 4: Create Script to Populate Embeddings (1 hour)

**File**: `backend/scripts/populate_embeddings.py`

```python
"""
Populate embeddings for all games in database

Usage:
    python -m scripts.populate_embeddings [--batch-size 100] [--limit 1000]
"""

import asyncio
import argparse
from typing import List, Dict, Any
from supabase import create_client, Client
from app.config import settings
from app.services.embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def populate_embeddings(
    batch_size: int = 100,
    limit: int = None
):
    """
    Generate and store embeddings for all games
    
    Args:
        batch_size: Number of games to process per batch
        limit: Max number of games to process (None = all)
    """
    # Initialize Supabase client
    db: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY
    )
    
    logger.info("Fetching games from database...")
    
    # Build query
    query = db.schema(settings.DATABASE_SCHEMA)\
        .table(settings.DATABASE_TABLE)\
        .select('appid, name, short_description, genres')
    
    if limit:
        query = query.limit(limit)
    
    # Fetch games
    response = query.execute()
    games = response.data
    
    if not games:
        logger.error("No games found in database")
        return
    
    total_games = len(games)
    logger.info(f"Found {total_games} games to process")
    
    # Process in batches
    processed = 0
    for i in range(0, total_games, batch_size):
        batch = games[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_games + batch_size - 1) // batch_size
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} games)...")
        
        # Generate embeddings for batch
        embeddings = EmbeddingService.encode_batch(batch)
        
        # Update each game with its embedding
        for game, embedding in zip(batch, embeddings):
            try:
                db.schema(settings.DATABASE_SCHEMA)\
                    .table(settings.DATABASE_TABLE)\
                    .update({'embedding': embedding})\
                    .eq('appid', game['appid'])\
                    .execute()
                
                processed += 1
                
            except Exception as e:
                logger.error(f"Failed to update game {game['appid']}: {e}")
        
        logger.info(f"✓ Batch {batch_num}/{total_batches} complete ({processed}/{total_games} total)")
    
    logger.info(f"\n✅ Successfully processed {processed}/{total_games} games!")


def main():
    parser = argparse.ArgumentParser(description='Populate game embeddings')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='Number of games per batch (default: 100)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of games to process (default: all)')
    
    args = parser.parse_args()
    
    asyncio.run(populate_embeddings(
        batch_size=args.batch_size,
        limit=args.limit
    ))


if __name__ == "__main__":
    main()
```

**Run it:**
```bash
# Process all games
python -m scripts.populate_embeddings

# Process only 100 games (for testing)
python -m scripts.populate_embeddings --limit 100

# Use smaller batch size
python -m scripts.populate_embeddings --batch-size 50
```

---

### Step 5: Update Search Service (1 hour)

**File**: `backend/app/services/search_service.py`

Add semantic search method:

```python
from app.services.embedding_service import EmbeddingService
from typing import List

class SearchService:
    # ... existing code ...
    
    async def semantic_search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 20,
        offset: int = 0,
        similarity_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Semantic search using pgvector
        
        Args:
            query: Search query
            filters: Optional filters
            limit: Results per page
            offset: Pagination offset
            similarity_threshold: Minimum cosine similarity (0-1)
        
        Returns:
            Search results with similarity scores
        """
        logger.info(f"Semantic search: query='{query}'")
        
        # Generate query embedding
        query_embedding = EmbeddingService.encode_query(query)
        
        # Build base query with cosine similarity
        # Note: pgvector uses <=> for cosine distance (lower is better)
        # similarity = 1 - distance
        query_builder = self.db.schema(settings.DATABASE_SCHEMA)\
            .table(settings.DATABASE_TABLE)\
            .select('*')\
            .order('embedding <=> query_embedding', ascending=True)  # Closest first
        
        # Apply filters
        if filters:
            query_builder = self._apply_filters(query_builder, filters)
        
        # Apply pagination
        query_builder = query_builder.range(offset, offset + limit - 1)
        
        # Execute query
        # Note: Supabase doesn't directly support embedding comparison in Python client
        # We need to use RPC function for this
        
        result = await self._execute_vector_search(
            query_embedding,
            filters,
            limit,
            offset
        )
        
        return self._format_search_results(result, query, filters, offset, limit)
    
    async def _execute_vector_search(
        self,
        query_embedding: List[float],
        filters: Optional[SearchFilters],
        limit: int,
        offset: int
    ):
        """Execute vector search using RPC function"""
        # This requires creating a PostgreSQL function
        # See Step 6 for the SQL function
        
        params = {
            'query_embedding': query_embedding,
            'match_limit': limit,
            'match_offset': offset
        }
        
        if filters:
            if filters.price_max:
                params['price_max'] = filters.price_max
            if filters.genres:
                params['genres_filter'] = filters.genres
            if filters.type:
                params['type_filter'] = filters.type
        
        result = self.db.rpc('search_games_semantic', params).execute()
        return result
```

---

### Step 6: Create PostgreSQL Function (30 minutes)

Run this in Supabase SQL Editor:

```sql
-- Create function for semantic search with filters
CREATE OR REPLACE FUNCTION steam.search_games_semantic(
    query_embedding vector(384),
    match_limit int DEFAULT 20,
    match_offset int DEFAULT 0,
    price_max int DEFAULT NULL,
    genres_filter text[] DEFAULT NULL,
    type_filter text DEFAULT NULL
)
RETURNS TABLE (
    appid bigint,
    name text,
    short_description text,
    price_cents int,
    genres jsonb,
    categories jsonb,
    release_date date,
    total_reviews int,
    type text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.appid,
        g.name,
        g.short_description,
        g.price_cents,
        g.genres,
        g.categories,
        g.release_date,
        g.total_reviews,
        g.type,
        1 - (g.embedding <=> query_embedding) as similarity
    FROM steam.games_prod g
    WHERE 
        g.embedding IS NOT NULL
        AND (price_max IS NULL OR g.price_cents <= price_max)
        AND (type_filter IS NULL OR g.type = type_filter)
        AND (
            genres_filter IS NULL 
            OR EXISTS (
                SELECT 1 
                FROM jsonb_array_elements_text(g.genres) genre
                WHERE genre = ANY(genres_filter)
            )
        )
    ORDER BY g.embedding <=> query_embedding
    LIMIT match_limit
    OFFSET match_offset;
END;
$$;
```

---

### Step 7: Add Hybrid Search (2 hours)

**File**: `backend/app/services/search_service.py`

```python
async def hybrid_search(
    self,
    query: str,
    filters: Optional[SearchFilters] = None,
    sort_by: SortBy = SortBy.RELEVANCE,
    limit: int = 20,
    offset: int = 0,
    alpha: float = 0.5  # 0 = pure semantic, 1 = pure BM25
) -> Dict[str, Any]:
    """
    Hybrid search combining BM25 and semantic search
    
    Args:
        query: Search query
        filters: Optional filters
        sort_by: Sort method (only RELEVANCE uses hybrid)
        limit: Results per page
        offset: Pagination offset
        alpha: Fusion weight (0=semantic, 1=BM25, 0.5=balanced)
    
    Returns:
        Fused search results
    """
    if sort_by != SortBy.RELEVANCE or not query.strip():
        # Fall back to regular search for non-relevance sorts
        return await self.search(query, filters, sort_by, offset, limit)
    
    # Get more results for fusion
    fetch_limit = 200
    
    # 1. BM25 Search
    bm25_results = await self.search(
        query, filters, SortBy.RELEVANCE, 0, fetch_limit
    )
    
    # 2. Semantic Search
    semantic_results = await self.semantic_search(
        query, filters, fetch_limit, 0
    )
    
    # 3. Reciprocal Rank Fusion
    fused_results = self._reciprocal_rank_fusion(
        bm25_results['results'],
        semantic_results['results'],
        alpha
    )
    
    # 4. Apply pagination
    paginated = fused_results[offset:offset + limit]
    
    return {
        'results': paginated,
        'total': len(fused_results),
        'offset': offset,
        'limit': limit,
        'query': query,
        'filters': filters,
        'search_type': 'hybrid'
    }

def _reciprocal_rank_fusion(
    self,
    bm25_results: List[Dict],
    semantic_results: List[Dict],
    alpha: float,
    k: int = 60
) -> List[Dict]:
    """
    Reciprocal Rank Fusion for hybrid search
    
    Formula: RRF_score = 1 / (k + rank)
    Final_score = alpha * BM25_RRF + (1-alpha) * Semantic_RRF
    """
    scores = {}
    game_data = {}
    
    # BM25 scores
    for rank, result in enumerate(bm25_results, start=1):
        game_id = result['game_id']
        scores[game_id] = alpha * (1.0 / (k + rank))
        game_data[game_id] = result
    
    # Semantic scores
    for rank, result in enumerate(semantic_results, start=1):
        game_id = result['game_id']
        if game_id in scores:
            scores[game_id] += (1 - alpha) * (1.0 / (k + rank))
        else:
            scores[game_id] = (1 - alpha) * (1.0 / (k + rank))
            game_data[game_id] = result
    
    # Sort by fused score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    # Build result list
    results = []
    for game_id in sorted_ids:
        result = game_data[game_id].copy()
        result['fusion_score'] = scores[game_id]
        results.append(result)
    
    return results
```

---

### Step 8: Update API Endpoint (15 minutes)

**File**: `backend/app/api/v1/search.py`

```python
@router.post(
    "/search/semantic",
    response_model=SearchResponse,
    summary="Semantic Search",
    description="Semantic search using pgvector embeddings"
)
async def semantic_search(
    request: SearchRequest,
    db: Client = Depends(get_db)
):
    """Semantic search endpoint"""
    search_service = SearchService(db)
    
    result = await search_service.semantic_search(
        query=request.query,
        filters=request.filters,
        limit=request.limit or 20,
        offset=request.offset or 0
    )
    
    return SearchResponse(**result)


@router.post(
    "/search/hybrid",
    response_model=SearchResponse,
    summary="Hybrid Search",
    description="Hybrid search combining BM25 and semantic search"
)
async def hybrid_search(
    request: SearchRequest,
    alpha: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Fusion weight (0=pure semantic, 1=pure BM25)"
    ),
    db: Client = Depends(get_db)
):
    """Hybrid search endpoint"""
    search_service = SearchService(db)
    
    result = await search_service.hybrid_search(
        query=request.query,
        filters=request.filters,
        sort_by=SortBy.RELEVANCE,
        limit=request.limit or 20,
        offset=request.offset or 0,
        alpha=alpha
    )
    
    return SearchResponse(**result)
```

---

## Configuration

**File**: `backend/app/config.py`

```python
# Semantic Search Configuration
SEMANTIC_SEARCH_ENABLED: bool = True
"""Enable semantic search with pgvector"""

EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
"""Sentence transformer model name"""

EMBEDDING_DIMENSION: int = 384
"""Embedding vector dimension"""

HYBRID_SEARCH_ALPHA: float = 0.5
"""Default fusion weight for hybrid search"""
```

---

## Testing

### Unit Tests

```python
# tests/test_embedding_service.py
def test_encode_game():
    game = {
        'name': 'Call of Duty',
        'short_description': 'Action shooter',
        'genres': ['Action', 'Shooter']
    }
    
    embedding = EmbeddingService.encode_game(game)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)


def test_encode_query_cached():
    query = "action shooter game"
    
    # First call
    emb1 = EmbeddingService.encode_query(query)
    
    # Second call (should be cached)
    emb2 = EmbeddingService.encode_query(query)
    
    assert emb1 == emb2  # Same result from cache
```

### Integration Tests

```bash
# Test embedding generation
python -m scripts.populate_embeddings --limit 10

# Verify embeddings in database
# Run in Supabase SQL Editor:
SELECT 
    appid, 
    name, 
    embedding IS NOT NULL as has_embedding,
    array_length(embedding::float[], 1) as dimension
FROM steam.games_prod
LIMIT 10;
```

---

## Deployment Checklist

- [ ] Enable pgvector extension in Supabase
- [ ] Add embedding column to games_prod table
- [ ] Create vector index (ivfflat)
- [ ] Install dependencies (sentence-transformers, pgvector)
- [ ] Create PostgreSQL search function
- [ ] Populate embeddings for all games
- [ ] Update search service
- [ ] Add API endpoints
- [ ] Test semantic search
- [ ] Test hybrid search
- [ ] Update frontend to use new endpoints
- [ ] Monitor performance

---

## Performance Optimization

### 1. Index Tuning

```sql
-- Adjust number of lists based on dataset size
-- Rule of thumb: lists = sqrt(num_rows)
-- For 10,000 games: lists = 100
-- For 100,000 games: lists = 316

CREATE INDEX ON steam.games_prod 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 2. Batch Updates

When adding new games, update embeddings in batches:

```python
# Good: Batch update
new_games = [game1, game2, game3, ...]
embeddings = EmbeddingService.encode_batch(new_games)

# Bad: One at a time
for game in new_games:
    embedding = EmbeddingService.encode_game(game)
```

### 3. Query Caching

The `encode_query` method already uses `@lru_cache` to cache query embeddings.

---

## Timeline (Much Faster!)

| Task | Faiss | pgvector |
|------|-------|----------|
| Setup | 0.5 day | **2 min** ⚡ |
| Service | 1 day | **30 min** ⚡ |
| Index Build | 1 day | **1 hour** ⚡ |
| Search | 1 day | **1 hour** ⚡ |
| Fusion | 2 days | **2 hours** ⚡ |
| API | 1 day | **15 min** ⚡ |
| Testing | 2 days | **2 hours** ⚡ |
| **Total** | **8.5 days** | **~1 day** 🚀 |

---

## Cost Comparison

### Storage
- **Faiss**: Separate file storage (~100MB for 10K games)
- **pgvector**: In database (~150MB for 10K games, 384 dims)

### Memory
- **Faiss**: Full index in RAM (~100MB)
- **pgvector**: Managed by PostgreSQL (configurable)

### Maintenance
- **Faiss**: Rebuild index for updates
- **pgvector**: Simple UPDATE queries

---

## Troubleshooting

### Issue: "extension vector does not exist"
**Solution**: Enable in Supabase Dashboard or run `CREATE EXTENSION vector;`

### Issue: "column embedding does not exist"
**Solution**: Run the ALTER TABLE command to add the column

### Issue: Slow search performance
**Solution**: 
1. Ensure index is created
2. Increase `lists` parameter in index
3. Run `ANALYZE steam.games_prod;`

### Issue: Out of memory during embedding generation
**Solution**: Reduce batch size in populate_embeddings script

---

## Next Steps

1. ✅ Enable pgvector extension
2. ⏭️ Add embedding column
3. ⏭️ Install dependencies
4. ⏭️ Create embedding service
5. ⏭️ Populate embeddings (start with 100 games)
6. ⏭️ Test semantic search
7. ⏭️ Implement hybrid search
8. ⏭️ Update frontend

---

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai/vector-embeddings)
- [Sentence Transformers](https://www.sbert.net/)

