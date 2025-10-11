# search_games

## search_games

**Category:** API Endpoint
**Complexity:** High
**Last Updated:** 2024-10-08

### Description
Main search endpoint that implements the unified game search functionality. This function combines BM25 keyword search with semantic vector search using Faiss, applies fusion ranking algorithm, and returns paginated results with comprehensive game information.

### Signature
```python
@app.post("/api/v1/search/games", response_model=GameResultSchema)
async def search_games(query: SearchQuerySchema) -> GameResultSchema:
```

### Parameters
- `query` (SearchQuerySchema, required): Pydantic model containing:
  - `query` (str): User search text
  - `filters` (Optional[SearchFilters]): Filter criteria
    - `price_max` (Optional[int]): Maximum price in USD
    - `coop_type` (Optional[CoopType]): Multiplayer type filter
    - `platform` (Optional[List[Platform]]): Platform compatibility
  - `limit` (Optional[int]): Results per page (default: 20, max: 100)
  - `offset` (Optional[int]): Pagination offset (default: 0)

### Returns
- `GameResultSchema`: Pydantic response model containing:
  - `results` (List[GameResult]): Array of matching games with scores
  - `total` (int): Total number of matching games
  - `offset` (int): Current pagination offset
  - `limit` (int): Results per page
  - `query` (str): Original search query
  - `filters` (SearchFilters): Applied filters

### Example
```python
# FastAPI endpoint implementation
@app.post("/api/v1/search/games", response_model=GameResultSchema)
async def search_games(query: SearchQuerySchema) -> GameResultSchema:
    try:
        # 1. Validate and sanitize input
        clean_query = validate_search_query(query.query)
        
        # 2. Perform parallel searches
        bm25_results = await search_bm25_index(clean_query, query.limit * 2)
        semantic_results = await search_faiss_index(clean_query, query.limit * 2)
        
        # 3. Merge and rank results
        merged_results = merge_search_results(bm25_results, semantic_results)
        ranked_results = apply_fusion_ranking(merged_results)
        
        # 4. Apply filters
        filtered_results = apply_search_filters(ranked_results, query.filters)
        
        # 5. Paginate and return
        paginated_results = paginate_results(
            filtered_results, 
            query.offset, 
            query.limit
        )
        
        return GameResultSchema(
            results=paginated_results,
            total=len(filtered_results),
            offset=query.offset,
            limit=query.limit,
            query=query.query,
            filters=query.filters or {}
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal search error")
```

### Notes
- Implements comprehensive error handling with proper HTTP status codes
- Uses async/await for non-blocking I/O operations
- Applies rate limiting to prevent abuse
- Logs search queries for analytics and debugging
- Caches frequent searches for improved performance

### Related Functions
- [search_bm25_index](#search_bm25_index)
- [search_faiss_index](#search_faiss_index)
- [apply_fusion_ranking](#apply_fusion_ranking)
- [validate_search_query](#validate_search_query)

### Tags
#fastapi #endpoint #search #ranking #pagination

---
