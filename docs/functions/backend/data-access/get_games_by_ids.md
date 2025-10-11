# get_games_by_ids

## get_games_by_ids

**Category:** Data Access
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Efficiently retrieves multiple games from the database using a list of Steam game IDs. Optimized for bulk operations with proper batching to avoid SQL query length limits and maintain performance.

### Signature
```python
async def get_games_by_ids(game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
```

### Parameters
- `game_ids` (List[int], required): List of Steam game IDs to retrieve
- `batch_size` (int, optional): Number of IDs to process per batch (default: 100)

### Returns
- `List[GameInfo]`: List of GameInfo models for found games (may be fewer than requested)

### Example
```python
from typing import List
import sqlite3

async def get_games_by_ids(game_ids: List[int], batch_size: int = 100) -> List[GameInfo]:
    """
    Retrieve multiple games by their IDs with batching
    """
    if not game_ids:
        return []
    
    try:
        all_games = []
        
        # Process in batches to avoid SQL query length limits
        for i in range(0, len(game_ids), batch_size):
            batch_ids = game_ids[i:i + batch_size]
            batch_games = await _get_games_batch(batch_ids)
            all_games.extend(batch_games)
        
        return all_games
        
    except Exception as e:
        logger.error(f"Error retrieving games by IDs: {str(e)}")
        return []

async def _get_games_batch(game_ids: List[int]) -> List[GameInfo]:
    """Process a single batch of game IDs"""
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create placeholders for IN clause
            placeholders = ','.join('?' * len(game_ids))
            
            query = f"""
            SELECT 
                game_id, title, description, price, genres,
                coop_type, deck_comp, review_status, release_date,
                developer, publisher
            FROM games 
            WHERE game_id IN ({placeholders})
            ORDER BY game_id
            """
            
            cursor.execute(query, game_ids)
            rows = cursor.fetchall()
            
            games = []
            for row in rows:
                game_data = {
                    'game_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'price': row[3],
                    'genres': json.loads(row[4]) if row[4] else [],
                    'coop_type': row[5],
                    'deck_comp': bool(row[6]),
                    'review_status': row[7],
                    'release_date': row[8],
                    'developer': row[9],
                    'publisher': row[10]
                }
                games.append(GameInfo(**game_data))
            
            return games
            
    except sqlite3.Error as e:
        logger.error(f"Database error in batch retrieval: {str(e)}")
        return []
```

### Notes
- Batches requests to avoid SQLite query length limits
- Maintains order of results when possible
- Gracefully handles missing games (no exceptions for not found)
- Uses IN clause for efficient bulk retrieval
- Configurable batch size for performance tuning

### Related Functions
- [get_game_by_id](#get_game_by_id)
- [apply_search_filters](#apply_search_filters)
- [merge_search_results](#merge_search_results)

### Tags
#database #bulk-operations #batching #performance #sqlite

---
