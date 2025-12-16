
# 🔧 Create PostgreSQL Functions in Supabase

## Quick Steps

1. **Open Supabase SQL Editor:**
   - Go to: https://supabase.com/dashboard
   - Select your project
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

2. **Copy and paste the SQL below:**

```sql
-- ============================================================================
-- Step 1: Ensure pgvector extension is enabled
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Step 2: Create semantic search function with filters
-- ============================================================================
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

-- ============================================================================
-- Step 3: Create simple version for testing
-- ============================================================================
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

-- ============================================================================
-- Step 4: Grant permissions
-- ============================================================================
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO anon;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO anon;
```

3. **Click "Run" (or press Ctrl+Enter)**

4. **Verify success:**
   - You should see: "Success. No rows returned"
   - This is normal for CREATE FUNCTION statements

## ✅ Verification

After creating the functions, verify they work:

```sql
-- Test query (replace with actual embedding)
SELECT * FROM steam.search_games_semantic_simple(
    '[0.1, 0.2, ...]'::vector(384),
    5
);
```

## 🚀 Next Steps

After creating the functions, test the full semantic search:

```bash
cd backend
source venv/bin/activate
python -m scripts.test_semantic_search
```

