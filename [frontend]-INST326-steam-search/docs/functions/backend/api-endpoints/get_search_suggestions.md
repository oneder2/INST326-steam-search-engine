# get_search_suggestions

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
