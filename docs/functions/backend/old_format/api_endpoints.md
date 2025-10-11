# FastAPI Backend - API Endpoints

This document contains documentation for all FastAPI endpoint functions in the Steam Game Search Engine backend.

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

## get_search_suggestions

**Category:** API Endpoint
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Provides autocomplete suggestions based on partial user input. Uses a combination of popular search terms, game titles, and genre suggestions to help users discover relevant search queries.

### Signature
```python
@app.get("/api/v1/search/suggest", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(prefix: str = Query(..., min_length=1)) -> SearchSuggestionsResponse:
```

### Parameters
- `prefix` (str, required): Partial search text (minimum 1 character)

### Returns
- `SearchSuggestionsResponse`: Response containing:
  - `suggestions` (List[str]): Array of suggested search terms
  - `prefix` (str): Input prefix that generated suggestions

### Example
```python
@app.get("/api/v1/search/suggest", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(prefix: str = Query(..., min_length=1)) -> SearchSuggestionsResponse:
    try:
        # Sanitize input
        clean_prefix = sanitize_input(prefix.lower().strip())
        
        suggestions = []
        
        # 1. Game title suggestions
        title_suggestions = await get_game_title_suggestions(clean_prefix, limit=3)
        suggestions.extend(title_suggestions)
        
        # 2. Genre suggestions
        genre_suggestions = await get_genre_suggestions(clean_prefix, limit=2)
        suggestions.extend(genre_suggestions)
        
        # 3. Popular search patterns
        pattern_suggestions = await get_search_pattern_suggestions(clean_prefix, limit=3)
        suggestions.extend(pattern_suggestions)
        
        # 4. Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))[:10]
        
        return SearchSuggestionsResponse(
            suggestions=unique_suggestions,
            prefix=prefix
        )
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return SearchSuggestionsResponse(suggestions=[], prefix=prefix)
```

### Notes
- Implements fuzzy matching for typo tolerance
- Caches suggestions for 1 hour to improve performance
- Returns maximum 10 suggestions to avoid overwhelming users
- Gracefully handles errors by returning empty suggestions

### Related Functions
- [get_game_title_suggestions](#get_game_title_suggestions)
- [get_genre_suggestions](#get_genre_suggestions)
- [sanitize_input](#sanitize_input)

### Tags
#fastapi #endpoint #suggestions #autocomplete #cache

---

## get_game_detail

**Category:** API Endpoint
**Complexity:** Low
**Last Updated:** 2024-10-08

### Description
Retrieves comprehensive information about a specific game using its Steam game ID. Returns detailed metadata, quality metrics, and additional information not available in search results.

### Signature
```python
@app.get("/api/v1/games/{game_id}", response_model=GameDetailResponse)
async def get_game_detail(game_id: int = Path(..., gt=0)) -> GameDetailResponse:
```

### Parameters
- `game_id` (int, required): Steam game ID (must be positive integer)

### Returns
- `GameDetailResponse`: Comprehensive game information including all GameInfo fields plus:
  - `ranking_metrics` (RankingMetrics): Quality scores
  - `full_description` (Optional[str]): Extended description
  - `screenshots` (Optional[List[str]]): Screenshot URLs
  - `developer` (Optional[str]): Developer name
  - `publisher` (Optional[str]): Publisher name

### Example
```python
@app.get("/api/v1/games/{game_id}", response_model=GameDetailResponse)
async def get_game_detail(game_id: int = Path(..., gt=0)) -> GameDetailResponse:
    try:
        # 1. Fetch basic game info from database
        game_info = await get_game_by_id(game_id)
        if not game_info:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # 2. Calculate ranking metrics
        ranking_metrics = await calculate_game_ranking_metrics(game_id)
        
        # 3. Fetch additional metadata
        additional_info = await get_additional_game_info(game_id)
        
        # 4. Combine all information
        return GameDetailResponse(
            **game_info.dict(),
            ranking_metrics=ranking_metrics,
            full_description=additional_info.get("full_description"),
            screenshots=additional_info.get("screenshots", []),
            developer=additional_info.get("developer"),
            publisher=additional_info.get("publisher")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Game detail error for ID {game_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch game details")
```

### Notes
- Validates game_id as positive integer using Path parameter
- Returns 404 for non-existent games
- Caches game details for 30 minutes
- Includes comprehensive error handling

### Related Functions
- [get_game_by_id](#get_game_by_id)
- [calculate_game_ranking_metrics](#calculate_game_ranking_metrics)
- [get_additional_game_info](#get_additional_game_info)

### Tags
#fastapi #endpoint #gamedetail #database #cache

---

## health_check

**Category:** API Endpoint
**Complexity:** Low
**Last Updated:** 2024-10-08

### Description
Health check endpoint for monitoring service availability and system status. Verifies database connectivity, search index availability, and overall system health.

### Signature
```python
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
```

### Parameters
None

### Returns
- `HealthResponse`: Health status information:
  - `status` (str): Overall health status ("healthy", "degraded", "unhealthy")
  - `timestamp` (int): Unix timestamp of health check
  - `services` (Dict[str, str]): Individual service statuses
  - `version` (str): API version

### Example
```python
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    timestamp = int(time.time())
    services = {}
    
    try:
        # Check database connectivity
        db_status = await check_database_health()
        services["database"] = "healthy" if db_status else "unhealthy"
        
        # Check search indices
        bm25_status = check_bm25_index_health()
        faiss_status = check_faiss_index_health()
        services["bm25_index"] = "healthy" if bm25_status else "unhealthy"
        services["faiss_index"] = "healthy" if faiss_status else "unhealthy"
        
        # Determine overall status
        unhealthy_services = [k for k, v in services.items() if v == "unhealthy"]
        
        if not unhealthy_services:
            overall_status = "healthy"
        elif len(unhealthy_services) < len(services):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            timestamp=timestamp,
            services=services,
            version=API_VERSION
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=timestamp,
            services={"error": str(e)},
            version=API_VERSION
        )
```

### Notes
- Always returns 200 status code (health info in response body)
- Performs quick checks to avoid timeout issues
- Used by load balancers and monitoring systems
- Logs health check failures for debugging

### Related Functions
- [check_database_health](#check_database_health)
- [check_bm25_index_health](#check_bm25_index_health)
- [check_faiss_index_health](#check_faiss_index_health)

### Tags
#fastapi #endpoint #health #monitoring #status
