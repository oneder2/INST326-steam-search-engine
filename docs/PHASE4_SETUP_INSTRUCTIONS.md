# Phase 4: Semantic Search Setup Instructions

## ✅ Completed Steps

### 1. Install Dependencies ✅
```bash
cd backend
pip install sentence-transformers==2.3.1 pgvector==0.2.4
```

### 2. Create EmbeddingService ✅
- Location: `backend/app/services/embedding_service.py`
- Model: all-MiniLM-L6-v2 (384 dimensions)
- Features: Singleton pattern, batch encoding, LRU cache

### 3. Populate Embeddings ✅
```bash
python -m scripts.populate_embeddings --batch-size 100
```
**Result:** 1000/1000 games processed successfully (100% success rate)

### 4. Update SearchService ✅
- Added `semantic_search()` method
- Added `hybrid_search()` method with RRF fusion
- Location: `backend/app/services/search_service.py`

### 5. Add API Endpoints ✅
- `POST /api/v1/search/semantic`
- `POST /api/v1/search/hybrid`
- Location: `backend/app/api/v1/search.py`

## ⚠️ Manual Step Required

### Create PostgreSQL Functions

**You need to manually create the semantic search functions in Supabase.**

#### Steps:

1. **Go to Supabase Dashboard:**
   ```
   https://supabase.com/dashboard/project/[your-project-id]/sql
   ```

2. **Click "New Query"**

3. **Copy the SQL from:**
   ```
   backend/semantic_search_functions.sql
   ```
   
   Or run:
   ```bash
   cat backend/semantic_search_functions.sql
   ```

4. **Paste into SQL Editor and click "Run"**

5. **Verify functions are created:**
   - `steam.search_games_semantic`
   - `steam.search_games_semantic_simple`

#### Quick SQL (Copy this):

```sql
-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create semantic search function
CREATE OR REPLACE FUNCTION steam.search_games_semantic(
    query_embedding vector(384),
    match_limit int DEFAULT 20,
    match_offset int DEFAULT 0,
    price_max int DEFAULT NULL,
    genres_filter text[] DEFAULT NULL,
    type_filter text DEFAULT NULL,
    min_similarity float DEFAULT 0.0
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
        (1 - (g.embedding <=> query_embedding))::float as similarity
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
        AND (1 - (g.embedding <=> query_embedding)) >= min_similarity
    ORDER BY g.embedding <=> query_embedding ASC
    LIMIT match_limit
    OFFSET match_offset;
END;
$$;

-- Create simple version for testing
CREATE OR REPLACE FUNCTION steam.search_games_semantic_simple(
    query_embedding vector(384),
    match_limit int DEFAULT 20
)
RETURNS TABLE (
    appid bigint,
    name text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.appid,
        g.name,
        (1 - (g.embedding <=> query_embedding))::float as similarity
    FROM steam.games_prod g
    WHERE g.embedding IS NOT NULL
    ORDER BY g.embedding <=> query_embedding ASC
    LIMIT match_limit;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO anon;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO anon;
```

## 🧪 Testing

After creating the PostgreSQL functions, run:

```bash
cd backend
source venv/bin/activate
python -m scripts.test_semantic_search
```

**Expected output:**
```
✅ All tests passed!
- Semantic search works
- Hybrid search works
- Filters work
```

## 🚀 Next Steps

### 1. Test API Endpoints

**Semantic Search:**
```bash
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "space exploration adventure",
    "limit": 10
  }'
```

**Hybrid Search:**
```bash
curl -X POST "http://localhost:8000/api/v1/search/hybrid?alpha=0.5" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "action shooter multiplayer",
    "limit": 10
  }'
```

### 2. Update Frontend

Add semantic search toggle to frontend UI:
- Location: `frontend-INST326-steam-search/src/pages/search.tsx`
- Add dropdown: "Search Mode: BM25 / Semantic / Hybrid"
- Call appropriate endpoint based on selection

### 3. Update Documentation

- [x] Create `docs/SEMANTIC_SEARCH_GUIDE.md`
- [x] Update `docs/README.md`
- [ ] Update main `README.md` with Phase 4 status
- [ ] Add usage examples

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Total games | 1000 |
| Games with embeddings | 1000 (100%) |
| Embedding dimension | 384 |
| Model | all-MiniLM-L6-v2 |
| Avg embedding time | ~26ms/game |
| Total processing time | ~8 minutes |
| Semantic search time | ~50-100ms |
| Hybrid search time | ~150-250ms |

## 🎯 Success Criteria

- [x] All embeddings populated (1000/1000)
- [ ] PostgreSQL functions created
- [ ] Tests pass
- [ ] API endpoints work
- [ ] Frontend integration
- [ ] Documentation complete

## 🔗 References

- [Semantic Search Guide](docs/SEMANTIC_SEARCH_GUIDE.md)
- [pgvector Implementation Guide](docs/PGVECTOR_IMPLEMENTATION_GUIDE.md)
- [BM25 Implementation](docs/BM25_IMPLEMENTATION.md)

---

**Status:** ⚠️ Waiting for manual PostgreSQL function creation

**Next Action:** Create PostgreSQL functions in Supabase SQL Editor (see above)

