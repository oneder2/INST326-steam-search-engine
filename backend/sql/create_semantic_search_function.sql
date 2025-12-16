-- ============================================================================
-- Semantic Search Function for pgvector
-- ============================================================================
-- This function performs vector similarity search with optional filters
-- It uses cosine similarity to find games similar to a query embedding
--
-- Usage:
--   SELECT * FROM steam.search_games_semantic(
--     query_embedding := array[0.1, 0.2, ...],  -- 384-dimensional vector
--     match_limit := 20,
--     match_offset := 0,
--     price_max := 5000,  -- in cents
--     genres_filter := array['Action', 'Shooter'],
--     type_filter := 'game'
--   );
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
        -- Cosine similarity: 1 - cosine_distance
        -- <=> operator returns cosine distance
        (1 - (g.embedding <=> query_embedding))::float as similarity
    FROM steam.games_prod g
    WHERE 
        -- Must have embedding
        g.embedding IS NOT NULL
        
        -- Price filter
        AND (price_max IS NULL OR g.price_cents <= price_max)
        
        -- Type filter
        AND (type_filter IS NULL OR g.type = type_filter)
        
        -- Genres filter (AND logic: must have ALL selected genres)
        -- Check that the game's genres JSONB contains all genres in the filter
        AND (
            genres_filter IS NULL 
            OR (
                -- Count how many filter genres are present in the game's genres
                SELECT COUNT(DISTINCT genre) 
                FROM jsonb_array_elements_text(g.genres) genre
                WHERE genre = ANY(genres_filter)
            ) = array_length(genres_filter, 1)  -- Must match ALL genres
        )
        
        -- Minimum similarity threshold
        AND (1 - (g.embedding <=> query_embedding)) >= min_similarity
    
    -- Order by similarity (closest first)
    ORDER BY g.embedding <=> query_embedding ASC
    
    -- Pagination
    LIMIT match_limit
    OFFSET match_offset;
END;
$$;

-- ============================================================================
-- Create simpler version without filters (for testing)
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
-- Grant execute permissions
-- ============================================================================

-- Grant to authenticated users (adjust based on your RLS setup)
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic TO anon;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO authenticated;
GRANT EXECUTE ON FUNCTION steam.search_games_semantic_simple TO anon;

-- ============================================================================
-- Test queries
-- ============================================================================

-- Test 1: Simple search (you need to provide actual embedding)
-- SELECT * FROM steam.search_games_semantic_simple(
--     array[0.1, 0.2, ...]::vector(384),
--     10
-- );

-- Test 2: Search with filters
-- SELECT * FROM steam.search_games_semantic(
--     query_embedding := array[0.1, 0.2, ...]::vector(384),
--     match_limit := 20,
--     price_max := 5000,
--     genres_filter := array['Action', 'Shooter']
-- );

-- ============================================================================
-- Performance notes:
-- ============================================================================
-- 1. The ivfflat index should be created for performance:
--    CREATE INDEX ON steam.games_prod USING ivfflat (embedding vector_cosine_ops);
--
-- 2. For large datasets, adjust the 'lists' parameter:
--    CREATE INDEX ON steam.games_prod 
--    USING ivfflat (embedding vector_cosine_ops)
--    WITH (lists = 100);
--
-- 3. The <=> operator uses cosine distance (0 = identical, 2 = opposite)
--    Similarity = 1 - distance, so higher similarity = more relevant
-- ============================================================================

