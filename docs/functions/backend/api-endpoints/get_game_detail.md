# get_game_detail

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
