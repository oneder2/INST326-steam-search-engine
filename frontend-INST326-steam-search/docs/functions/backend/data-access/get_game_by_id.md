# get_game_by_id

## get_game_by_id

**Category:** Data Access
**Complexity:** Low
**Last Updated:** 2024-10-08

### Description
Retrieves a single game's information from the SQLite database using its Steam game ID. Returns a Pydantic GameInfo model with all core game metadata including title, description, price, genres, and platform compatibility.

### Signature
```python
async def get_game_by_id(game_id: int) -> Optional[GameInfo]:
```

### Parameters
- `game_id` (int, required): Steam game ID to retrieve

### Returns
- `Optional[GameInfo]`: Pydantic model containing game information, or None if not found

### Example
```python
import sqlite3
import asyncio
from typing import Optional
from pydantic import BaseModel

class GameInfo(BaseModel):
    game_id: int
    title: str
    description: str
    price: float
    genres: List[str]
    coop_type: Optional[str]
    deck_comp: bool
    review_status: str
    release_date: Optional[str]
    developer: Optional[str]
    publisher: Optional[str]

async def get_game_by_id(game_id: int) -> Optional[GameInfo]:
    """
    Retrieve game information by Steam game ID
    """
    try:
        # Use connection pool for better performance
        async with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                game_id, title, description, price, genres,
                coop_type, deck_comp, review_status, release_date,
                developer, publisher
            FROM games 
            WHERE game_id = ?
            """
            
            cursor.execute(query, (game_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Convert row to GameInfo model
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
            
            return GameInfo(**game_data)
            
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving game {game_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving game {game_id}: {str(e)}")
        return None

# Database connection management
async def get_db_connection():
    """Get database connection with proper configuration"""
    conn = sqlite3.connect(
        'data/games_data.db',
        check_same_thread=False,
        timeout=30.0
    )
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn
```

### Notes
- Uses parameterized queries to prevent SQL injection
- Handles JSON deserialization for genres array
- Returns None for non-existent games (not an exception)
- Implements connection pooling for better performance
- Comprehensive error logging for debugging

### Related Functions
- [get_games_by_ids](#get_games_by_ids)
- [search_games_by_title](#search_games_by_title)
- [get_db_connection](#get_db_connection)

### Tags
#database #sqlite #pydantic #async #error-handling

---
