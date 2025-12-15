# Search Implementation Roadmap

**Based on Database Schema Analysis**  
**Date:** December 15, 2025

---

## Database Schema Analysis

### Available Fields for Search

```sql
-- Text fields (for search)
name text NOT NULL                    -- Primary search target
short_description text                -- Secondary search target
detailed_desc text                    -- Detailed search target
search_tsv text                       -- ⭐ Pre-computed search vector!

-- Filter fields
genres jsonb                          -- Multi-select filter
categories jsonb                      -- Multi-select filter
type text (INDEXED)                   -- Type filter (game/dlc/etc)
price_cents integer (INDEXED)         -- Price range filter
release_date date                     -- Date range filter

-- Ranking/Sorting fields
total_reviews integer                 -- Popularity indicator
dlc_count integer                     -- Content richness
price_cents integer                   -- Price sorting
release_date date                     -- Recency sorting
```

### Key Discovery: `search_tsv` Field

This field suggests the database already has **PostgreSQL full-text search** support prepared!

**Likely format:** tsvector or pre-computed text search tokens

---

## Implementation Phases

### 📊 Complexity vs Impact Matrix

```
Impact
  │
  │  Phase 3         Phase 5
  │  [Filters]       [Semantic]
  │     │               │
  │     │               │
  │  Phase 2         Phase 4
  │  [Full-text]     [BM25]
  │     │               │
  │     │               │
  │  Phase 1         
  │  [Basic Search]  
  │
  └─────────────────────────── Complexity
     Simple              Complex
```

---

## Phase 1: Basic Text Search (Simple LIKE/ILIKE)

### 🎯 Goal
Implement basic keyword search in game names

### 📝 Implementation

**Backend Endpoint:**
```python
# POST /api/v1/search/basic
async def basic_search(query: str, offset: int = 0, limit: int = 20):
    # Simple ILIKE search on name field
    result = db.table(settings.DATABASE_TABLE)\
        .select('*')\
        .ilike('name', f'%{query}%')\
        .range(offset, offset + limit - 1)\
        .execute()
    return result
```

**SQL Equivalent:**
```sql
SELECT * FROM steam.games_prod 
WHERE name ILIKE '%user_query%'
ORDER BY name
LIMIT 20 OFFSET 0;
```

### ✅ Advantages
- Very simple to implement (30 minutes)
- No algorithm complexity
- Works immediately
- Good for exact name searches

### ❌ Limitations
- Case-insensitive only
- No relevance ranking
- No multi-field search
- Poor for partial matches
- No synonym support

### 📊 Use Case
User searches: "call of duty" → Finds "Call of Duty®" games

---

## Phase 2: PostgreSQL Full-Text Search (Use search_tsv)

### 🎯 Goal
Implement proper full-text search using the `search_tsv` field

### 📝 Implementation

**Step 1: Understand search_tsv Format**

First, check what's in the field:
```sql
SELECT appid, name, search_tsv FROM steam.games_prod LIMIT 1;
```

**Step 2A: If search_tsv is tsvector (PostgreSQL native)**

```python
# Backend implementation
async def fulltext_search(query: str, offset: int = 0, limit: int = 20):
    # Use PostgreSQL's @@ operator for tsvector search
    # Note: Supabase may need RPC function for this
    
    result = db.rpc('search_games', {
        'search_query': query,
        'offset_val': offset,
        'limit_val': limit
    }).execute()
    return result
```

Create Supabase RPC function:
```sql
CREATE OR REPLACE FUNCTION search_games(
    search_query text,
    offset_val integer DEFAULT 0,
    limit_val integer DEFAULT 20
)
RETURNS TABLE (
    appid bigint,
    name text,
    price_cents integer,
    genres jsonb,
    -- ... other fields
    rank real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.*,
        ts_rank(g.search_tsv::tsvector, plainto_tsquery('english', search_query)) as rank
    FROM steam.games_prod g
    WHERE g.search_tsv::tsvector @@ plainto_tsquery('english', search_query)
    ORDER BY rank DESC, g.total_reviews DESC
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
```

**Step 2B: If search_tsv is plain text (tokens)**

```python
# Simpler approach using text matching
async def fulltext_search(query: str, offset: int = 0, limit: int = 20):
    # Split query into tokens
    tokens = query.lower().split()
    
    # Build filter for each token
    query_builder = db.table(settings.DATABASE_TABLE).select('*')
    
    for token in tokens:
        query_builder = query_builder.ilike('search_tsv', f'%{token}%')
    
    result = query_builder\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return result
```

### ✅ Advantages
- Much better relevance ranking
- Handles word stemming (run/running/ran)
- Multi-field search (name + description)
- Fast with proper indexes
- Supports boolean operators

### ❌ Limitations
- Requires understanding search_tsv format
- May need database RPC function
- Still no semantic understanding

### 📊 Use Case
User searches: "strategy war" → Finds all strategy war games ranked by relevance

---

## Phase 3: Filters and Sorting

### 🎯 Goal
Add filtering by genre, price, type, etc.

### 📝 Implementation

**Backend Model:**
```python
class SearchFilters(BaseModel):
    # Price filters
    price_min: Optional[int] = None  # in cents
    price_max: Optional[int] = None  # in cents
    
    # Genre/Category filters (use JSONB containment)
    genres: Optional[List[str]] = None  # ["Action", "RPG"]
    categories: Optional[List[str]] = None
    
    # Type filter (use index!)
    type: Optional[str] = None  # "game", "dlc", etc.
    
    # Date filters
    release_date_after: Optional[date] = None
    release_date_before: Optional[date] = None
    
    # Other filters
    has_reviews: Optional[bool] = None  # total_reviews > 0
    min_reviews: Optional[int] = None

class SearchSort(str, Enum):
    RELEVANCE = "relevance"  # Default
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    REVIEWS = "reviews"      # Most reviewed
    NEWEST = "newest"
    OLDEST = "oldest"
```

**SQL Example with Filters:**
```sql
SELECT * FROM steam.games_prod
WHERE 
    search_tsv @@ plainto_tsquery('english', 'action game')
    AND price_cents BETWEEN 0 AND 2000  -- $0-$20
    AND genres @> '["Action"]'::jsonb   -- Contains "Action"
    AND type = 'game'                    -- Use index
    AND total_reviews >= 100
ORDER BY ts_rank(search_tsv, plainto_tsquery('english', 'action game')) DESC
LIMIT 20 OFFSET 0;
```

**Backend Implementation:**
```python
async def search_with_filters(
    query: str,
    filters: SearchFilters,
    sort: SearchSort = SearchSort.RELEVANCE,
    offset: int = 0,
    limit: int = 20
):
    # Build base query
    db_query = db.table(settings.DATABASE_TABLE).select('*')
    
    # Apply text search (if query provided)
    if query:
        db_query = db_query.ilike('search_tsv', f'%{query}%')
    
    # Apply price filter (use index!)
    if filters.price_min is not None:
        db_query = db_query.gte('price_cents', filters.price_min)
    if filters.price_max is not None:
        db_query = db_query.lte('price_cents', filters.price_max)
    
    # Apply type filter (use index!)
    if filters.type:
        db_query = db_query.eq('type', filters.type)
    
    # Apply genre filter (JSONB contains)
    if filters.genres:
        for genre in filters.genres:
            db_query = db_query.contains('genres', [genre])
    
    # Apply date filters
    if filters.release_date_after:
        db_query = db_query.gte('release_date', filters.release_date_after)
    if filters.release_date_before:
        db_query = db_query.lte('release_date', filters.release_date_before)
    
    # Apply review filters
    if filters.min_reviews:
        db_query = db_query.gte('total_reviews', filters.min_reviews)
    
    # Apply sorting
    if sort == SearchSort.PRICE_ASC:
        db_query = db_query.order('price_cents', desc=False)
    elif sort == SearchSort.PRICE_DESC:
        db_query = db_query.order('price_cents', desc=True)
    elif sort == SearchSort.REVIEWS:
        db_query = db_query.order('total_reviews', desc=True)
    elif sort == SearchSort.NEWEST:
        db_query = db_query.order('release_date', desc=True)
    elif sort == SearchSort.OLDEST:
        db_query = db_query.order('release_date', desc=False)
    
    # Apply pagination
    result = db_query.range(offset, offset + limit - 1).execute()
    
    return result
```

### ✅ Advantages
- Uses existing database indexes
- Very fast filtering
- Flexible combination of filters
- Good user experience

### ❌ Limitations
- No advanced relevance scoring
- JSONB queries may be slower for complex filters

### 📊 Use Case
User searches: "RPG" + filter by price < $20 + sort by reviews

---

## Phase 4: BM25 Ranking Algorithm

### 🎯 Goal
Implement industry-standard BM25 for better relevance ranking

### 📝 Implementation

**What is BM25?**
BM25 (Best Matching 25) is a ranking function that considers:
- Term frequency (TF): How often does the search term appear?
- Inverse document frequency (IDF): How rare is the term?
- Document length normalization: Longer docs don't dominate

**Formula:**
```
score(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))

Where:
- D = document (game)
- Q = query
- qi = query term i
- f(qi, D) = term frequency in document
- |D| = document length
- avgdl = average document length
- k1 = 1.5 (tuning parameter)
- b = 0.75 (length normalization)
```

**Implementation Options:**

**Option A: Python Implementation (Backend)**
```python
from rank_bm25 import BM25Okapi
import numpy as np

class BM25SearchService:
    def __init__(self):
        self.bm25 = None
        self.games = []
        self.tokenized_corpus = []
    
    async def initialize(self, db_client: Client):
        """Load all games and build BM25 index"""
        # Get all games
        result = db_client.table(settings.DATABASE_TABLE)\
            .select('appid, name, short_description, detailed_desc')\
            .execute()
        
        self.games = result.data
        
        # Tokenize corpus
        self.tokenized_corpus = [
            self._tokenize(
                f"{game['name']} {game['short_description'] or ''} "
                f"{game['detailed_desc'] or ''}"
            )
            for game in self.games
        ]
        
        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return text.lower().split()
    
    async def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search using BM25"""
        # Tokenize query
        tokenized_query = self._tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top N indices
        top_indices = np.argsort(scores)[::-1]
        
        # Filter and return results
        results = []
        for idx in top_indices:
            if len(results) >= limit:
                break
            
            game = self.games[idx]
            score = scores[idx]
            
            # Apply filters if provided
            if filters and not self._matches_filters(game, filters):
                continue
            
            results.append({
                **game,
                'bm25_score': float(score)
            })
        
        return results
```

**Option B: PostgreSQL Function (Database)**
```sql
-- Use PostgreSQL's built-in text search ranking
-- This is actually similar to BM25

CREATE OR REPLACE FUNCTION bm25_search(
    search_query text,
    offset_val integer DEFAULT 0,
    limit_val integer DEFAULT 20
)
RETURNS TABLE (
    appid bigint,
    name text,
    -- ... other fields
    bm25_score real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.*,
        ts_rank_cd(
            g.search_tsv::tsvector,
            plainto_tsquery('english', search_query),
            32  -- Use document length normalization (similar to BM25)
        ) as bm25_score
    FROM steam.games_prod g
    WHERE g.search_tsv::tsvector @@ plainto_tsquery('english', search_query)
    ORDER BY bm25_score DESC
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
```

### ✅ Advantages
- Industry-standard ranking
- Better relevance than simple TF-IDF
- Handles document length well
- Fast enough for real-time search

### ❌ Limitations
- Requires loading corpus into memory (Python) or complex SQL
- Still no semantic understanding
- May need periodic re-indexing

### 📊 Use Case
User searches: "indie puzzle game" → Results ranked by BM25 relevance

---

## Phase 5: Semantic Search with Faiss

### 🎯 Goal
Understand search intent using embeddings and vector similarity

### 📝 Implementation

**Architecture:**
```
User Query: "games like dark souls"
    ↓
1. Generate embedding (384 dimensions)
    ↓
2. Search Faiss index for similar games
    ↓
3. Combine with BM25 score (hybrid)
    ↓
4. Return ranked results
```

**Backend Implementation:**
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticSearchService:
    def __init__(self):
        # Use lightweight model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dim
        self.index = None
        self.games = []
    
    async def initialize(self, db_client: Client):
        """Build Faiss index from game descriptions"""
        # Get all games
        result = db_client.table(settings.DATABASE_TABLE)\
            .select('*')\
            .execute()
        
        self.games = result.data
        
        # Generate embeddings
        texts = [
            f"{game['name']} {game['short_description'] or ''}"
            for game in self.games
        ]
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = embeddings.astype('float32')
        
        # Build Faiss index
        dimension = embeddings.shape[1]  # 384
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
    
    async def search(
        self,
        query: str,
        k: int = 100,  # Get top 100 for re-ranking
        filters: Optional[SearchFilters] = None
    ) -> List[Dict]:
        """Semantic search using Faiss"""
        # Generate query embedding
        query_embedding = self.model.encode([query]).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        # Convert to results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            game = self.games[idx]
            
            # Apply filters
            if filters and not self._matches_filters(game, filters):
                continue
            
            results.append({
                **game,
                'semantic_score': float(distance)
            })
        
        return results
```

**Hybrid Search (BM25 + Semantic):**
```python
class HybridSearchService:
    def __init__(self, bm25_service, semantic_service):
        self.bm25 = bm25_service
        self.semantic = semantic_service
    
    async def search(
        self,
        query: str,
        alpha: float = 0.5,  # Weight: 0.5 = equal, 1.0 = BM25 only, 0.0 = semantic only
        limit: int = 20
    ) -> List[Dict]:
        """Hybrid search combining BM25 and semantic"""
        # Get results from both
        bm25_results = await self.bm25.search(query, limit=100)
        semantic_results = await self.semantic.search(query, k=100)
        
        # Normalize scores
        bm25_scores = self._normalize_scores([r['bm25_score'] for r in bm25_results])
        semantic_scores = self._normalize_scores([r['semantic_score'] for r in semantic_results])
        
        # Combine scores
        combined = {}
        for i, result in enumerate(bm25_results):
            appid = result['appid']
            combined[appid] = {
                **result,
                'hybrid_score': alpha * bm25_scores[i]
            }
        
        for i, result in enumerate(semantic_results):
            appid = result['appid']
            if appid in combined:
                combined[appid]['hybrid_score'] += (1 - alpha) * semantic_scores[i]
            else:
                combined[appid] = {
                    **result,
                    'hybrid_score': (1 - alpha) * semantic_scores[i]
                }
        
        # Sort by hybrid score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        return sorted_results[:limit]
```

### ✅ Advantages
- Understands semantic meaning
- Handles "games like X" queries
- Works with synonyms
- Best user experience

### ❌ Limitations
- Requires ML model (CPU/GPU)
- Larger memory footprint
- Slower than pure SQL
- Need to store/update embeddings

### 📊 Use Case
User searches: "atmospheric horror adventure" → Finds games with similar vibes

---

## Recommended Implementation Order

### Week 1-2: Phase 1 + Phase 3 (Quick Wins)
1. Implement basic ILIKE search on `name` field
2. Add price, genre, type filters
3. Add sorting options
4. **Result:** Functional search with filters

### Week 3: Phase 2 (Improve Relevance)
1. Investigate `search_tsv` field format
2. Implement full-text search
3. Add multi-field search (name + description)
4. **Result:** Better search relevance

### Week 4: Phase 4 (Professional Quality)
1. Implement BM25 ranking
2. Tune parameters (k1, b)
3. Test with real queries
4. **Result:** Industry-standard search

### Week 5+ (Optional): Phase 5 (Advanced)
1. Generate embeddings for all games
2. Build Faiss index
3. Implement hybrid search
4. **Result:** Semantic search capability

---

## Database Optimizations

### Additional Indexes to Create

```sql
-- Full-text search index (if search_tsv is tsvector)
CREATE INDEX idx_games_search_tsv ON steam.games_prod 
USING GIN (search_tsv);

-- Genre search (JSONB)
CREATE INDEX idx_games_genres ON steam.games_prod 
USING GIN (genres);

-- Category search (JSONB)
CREATE INDEX idx_games_categories ON steam.games_prod 
USING GIN (categories);

-- Compound index for common queries
CREATE INDEX idx_games_type_price ON steam.games_prod (type, price_cents);

-- Release date for sorting
CREATE INDEX idx_games_release_date ON steam.games_prod (release_date DESC);

-- Reviews for sorting/filtering
CREATE INDEX idx_games_reviews ON steam.games_prod (total_reviews DESC);
```

---

## Performance Considerations

### Phase 1-3 (SQL-based)
- **Latency:** < 100ms
- **Scalability:** Excellent (PostgreSQL handles it)
- **Memory:** Minimal (all in database)

### Phase 4 (BM25 in Python)
- **Latency:** 100-500ms
- **Scalability:** Good (may need caching)
- **Memory:** Medium (~500MB for 1000 games)

### Phase 5 (Faiss)
- **Latency:** 50-200ms (fast!)
- **Scalability:** Excellent with proper setup
- **Memory:** High (~1-2GB for embeddings)

---

## Testing Strategy

### For Each Phase

1. **Unit Tests:**
   - Test search function with various queries
   - Test filter combinations
   - Test edge cases (empty query, special chars)

2. **Integration Tests:**
   - Test full API endpoint
   - Test with real database
   - Test pagination

3. **Quality Tests:**
   - Relevance testing (manual)
   - Performance benchmarks
   - A/B testing (if possible)

### Example Test Cases

```python
# Phase 1 Tests
test_basic_search("call of duty", expected_count=10)
test_basic_search("xyz123notfound", expected_count=0)
test_basic_search("", expected_count=0)  # Empty query

# Phase 3 Tests
test_filter_by_price(max_price=1000, expected_all_below=True)
test_filter_by_genre(genres=["Action"], expected_all_have_action=True)
test_combined_filters(query="RPG", price_max=2000, genres=["RPG"])

# Phase 4 Tests
test_bm25_relevance(
    query="strategy war game",
    expected_top_result="Civilization VI"
)

# Phase 5 Tests
test_semantic_search(
    query="games like dark souls",
    expected_similar=["Elden Ring", "Bloodborne"]
)
```

---

## Summary

### Quick Start (MVP++) - Weeks 1-2
✅ Basic search + filters + sorting  
**Effort:** Low | **Impact:** High

### Professional Quality - Weeks 3-4
✅ Full-text search + BM25  
**Effort:** Medium | **Impact:** High

### Advanced (Optional) - Week 5+
✅ Semantic search with Faiss  
**Effort:** High | **Impact:** Medium (niche use case)

---

**Recommendation:** Start with Phase 1 + 3 (basic search + filters) to quickly provide value, then iterate to Phase 2 and 4 for better relevance.

---

**Next Steps:**
1. Choose which phase to implement first
2. Create API endpoint structure
3. Update frontend for search input
4. Implement and test


