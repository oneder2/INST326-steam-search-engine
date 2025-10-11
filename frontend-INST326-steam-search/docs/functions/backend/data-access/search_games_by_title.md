# search_games_by_title

## search_games_by_title

**Category:** Data Access
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Searches for games by title using SQL LIKE queries with fuzzy matching capabilities. Optimized for autocomplete suggestions and exact title lookups with support for partial matches and typo tolerance.

### Signature
```python
async def search_games_by_title(title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
```

### Parameters
- `title_query` (str, required): Title search query
- `limit` (int, optional): Maximum number of results to return (default: 10)
- `fuzzy` (bool, optional): Enable fuzzy matching for typos (default: True)

### Returns
- `List[GameInfo]`: List of games matching the title query

### Example
```python
import sqlite3
import re
from typing import List, Optional
from difflib import SequenceMatcher

async def search_games_by_title(title_query: str, limit: int = 10, fuzzy: bool = True) -> List[GameInfo]:
    """
    Search games by title with fuzzy matching support
    """
    try:
        if not title_query or not title_query.strip():
            return []
        
        # Sanitize and normalize query
        clean_query = sanitize_input(title_query.strip())
        
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Try exact and partial matches first
            exact_results = await _search_exact_title_matches(cursor, clean_query, limit)
            
            if len(exact_results) >= limit or not fuzzy:
                return exact_results[:limit]
            
            # If we need more results and fuzzy is enabled, try fuzzy matching
            remaining_limit = limit - len(exact_results)
            fuzzy_results = await _search_fuzzy_title_matches(
                cursor, clean_query, remaining_limit, exact_results
            )
            
            # Combine and deduplicate results
            all_results = exact_results + fuzzy_results
            unique_results = _deduplicate_games(all_results)
            
            return unique_results[:limit]
            
    except Exception as e:
        logger.error(f"Error searching games by title '{title_query}': {str(e)}")
        return []

async def _search_exact_title_matches(cursor, query: str, limit: int) -> List[GameInfo]:
    """Search for exact and partial title matches"""
    try:
        # Prepare search patterns
        exact_pattern = query.lower()
        partial_pattern = f"%{exact_pattern}%"
        word_pattern = f"%{exact_pattern.replace(' ', '%')}%"
        
        # SQL query with multiple matching strategies
        sql_query = """
        SELECT DISTINCT game_id, title, description, price, genres, 
               coop_type, deck_comp, review_status, release_date, 
               developer, publisher,
               CASE 
                   WHEN LOWER(title) = ? THEN 1
                   WHEN LOWER(title) LIKE ? THEN 2
                   WHEN LOWER(title) LIKE ? THEN 3
                   ELSE 4
               END as match_priority
        FROM games 
        WHERE LOWER(title) LIKE ?
        ORDER BY match_priority, title
        LIMIT ?
        """
        
        cursor.execute(sql_query, (
            exact_pattern,      # Exact match
            f"{exact_pattern}%", # Starts with
            partial_pattern,    # Contains
            word_pattern,       # Word-based match
            limit
        ))
        
        rows = cursor.fetchall()
        return [_row_to_game_info(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error in exact title search: {str(e)}")
        return []

async def _search_fuzzy_title_matches(cursor, query: str, limit: int, exclude_games: List[GameInfo]) -> List[GameInfo]:
    """Search for fuzzy title matches using similarity algorithms"""
    try:
        # Get existing game IDs to exclude
        exclude_ids = {game.game_id for game in exclude_games}
        
        # Get all game titles for fuzzy matching
        cursor.execute("SELECT game_id, title FROM games WHERE title IS NOT NULL")
        all_titles = cursor.fetchall()
        
        # Calculate similarity scores
        fuzzy_matches = []
        query_lower = query.lower()
        
        for game_id, title in all_titles:
            if game_id in exclude_ids:
                continue
            
            title_lower = title.lower()
            
            # Calculate similarity using different methods
            similarity_scores = [
                SequenceMatcher(None, query_lower, title_lower).ratio(),
                _calculate_word_similarity(query_lower, title_lower),
                _calculate_substring_similarity(query_lower, title_lower)
            ]
            
            # Use the best similarity score
            best_similarity = max(similarity_scores)
            
            # Only include if similarity is above threshold
            if best_similarity >= 0.6:  # 60% similarity threshold
                fuzzy_matches.append((game_id, title, best_similarity))
        
        # Sort by similarity score (descending)
        fuzzy_matches.sort(key=lambda x: x[2], reverse=True)
        
        # Get full game info for top matches
        top_matches = fuzzy_matches[:limit]
        if not top_matches:
            return []
        
        # Fetch full game information
        game_ids = [match[0] for match in top_matches]
        placeholders = ','.join('?' * len(game_ids))
        
        cursor.execute(f"""
            SELECT game_id, title, description, price, genres, 
                   coop_type, deck_comp, review_status, release_date, 
                   developer, publisher
            FROM games 
            WHERE game_id IN ({placeholders})
        """, game_ids)
        
        rows = cursor.fetchall()
        games_dict = {row[0]: _row_to_game_info(row) for row in rows}
        
        # Return games in similarity order
        return [games_dict[game_id] for game_id, _, _ in top_matches if game_id in games_dict]
        
    except Exception as e:
        logger.error(f"Error in fuzzy title search: {str(e)}")
        return []

def _calculate_word_similarity(query: str, title: str) -> float:
    """Calculate similarity based on word overlap"""
    query_words = set(query.split())
    title_words = set(title.split())
    
    if not query_words or not title_words:
        return 0.0
    
    intersection = query_words.intersection(title_words)
    union = query_words.union(title_words)
    
    return len(intersection) / len(union) if union else 0.0

def _calculate_substring_similarity(query: str, title: str) -> float:
    """Calculate similarity based on common substrings"""
    if not query or not title:
        return 0.0
    
    # Find longest common substring
    max_length = 0
    query_len = len(query)
    title_len = len(title)
    
    for i in range(query_len):
        for j in range(title_len):
            length = 0
            while (i + length < query_len and 
                   j + length < title_len and 
                   query[i + length] == title[j + length]):
                length += 1
            max_length = max(max_length, length)
    
    # Normalize by the length of the shorter string
    return max_length / min(query_len, title_len) if min(query_len, title_len) > 0 else 0.0

def _row_to_game_info(row) -> GameInfo:
    """Convert database row to GameInfo object"""
    return GameInfo(
        game_id=row[0],
        title=row[1],
        description=row[2] or "",
        price=row[3] or 0.0,
        genres=json.loads(row[4]) if row[4] else [],
        coop_type=row[5],
        deck_comp=bool(row[6]) if row[6] is not None else False,
        review_status=row[7] or "Unknown",
        release_date=row[8],
        developer=row[9],
        publisher=row[10]
    )

def _deduplicate_games(games: List[GameInfo]) -> List[GameInfo]:
    """Remove duplicate games based on game_id"""
    seen_ids = set()
    unique_games = []
    
    for game in games:
        if game.game_id not in seen_ids:
            seen_ids.add(game.game_id)
            unique_games.append(game)
    
    return unique_games

# Usage examples
# Exact title search
games = await search_games_by_title("Hades")

# Fuzzy search with typos
games = await search_games_by_title("Haides", fuzzy=True)

# Partial title search
games = await search_games_by_title("Dead", limit=5)
```

### Notes
- Implements multiple matching strategies: exact, partial, and fuzzy
- Uses similarity algorithms for typo tolerance
- Optimized SQL queries with proper indexing considerations
- Supports word-based and substring similarity calculations
- Includes deduplication and result ranking
- Configurable similarity thresholds for quality control

### Related Functions
- [get_game_by_id](#get_game_by_id)
- [sanitize_input](#sanitize_input)
- [get_search_suggestions](#get_search_suggestions)

### Tags
#database #search #fuzzy-matching #similarity #autocomplete #sql
