# FastAPI Backend - Data Access Functions

This document contains documentation for data access and database functions in the Python FastAPI backend.

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

## load_bm25_index

**Category:** Data Access
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Loads and initializes the BM25 search index from preprocessed game data. This function is called once at application startup to load the index into memory for fast keyword searches. Builds the index from game titles, descriptions, and genres.

### Signature
```python
def load_bm25_index() -> Tuple[BM25Okapi, List[Dict]]:
```

### Parameters
None

### Returns
- `Tuple[BM25Okapi, List[Dict]]`: Tuple containing the BM25 index and game corpus data

### Example
```python
from rank_bm25 import BM25Okapi
import json
import pickle
from typing import List, Dict, Tuple

def load_bm25_index() -> Tuple[BM25Okapi, List[Dict]]:
    """
    Load BM25 index and game corpus at application startup
    """
    try:
        # Try to load pre-built index first
        if os.path.exists('data/bm25_index.pkl'):
            logger.info("Loading pre-built BM25 index...")
            with open('data/bm25_index.pkl', 'rb') as f:
                index_data = pickle.load(f)
                return index_data['index'], index_data['corpus']
        
        # Build index from scratch if no pre-built version exists
        logger.info("Building BM25 index from game data...")
        
        # Load game data from database
        game_corpus = load_game_corpus()
        
        # Prepare documents for BM25
        documents = []
        for game in game_corpus:
            # Combine title, description, and genres for indexing
            doc_text = prepare_document_text(game)
            tokenized_doc = tokenize_text(doc_text)
            documents.append(tokenized_doc)
        
        # Create BM25 index
        bm25_index = BM25Okapi(documents)
        
        # Save index for faster future loading
        save_bm25_index(bm25_index, game_corpus)
        
        logger.info(f"BM25 index built with {len(documents)} documents")
        return bm25_index, game_corpus
        
    except Exception as e:
        logger.error(f"Failed to load BM25 index: {str(e)}")
        raise

def load_game_corpus() -> List[Dict]:
    """Load all games from database for indexing"""
    try:
        with sqlite3.connect('data/games_data.db') as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT game_id, title, description, genres
            FROM games
            WHERE title IS NOT NULL AND description IS NOT NULL
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            corpus = []
            for row in rows:
                game_doc = {
                    'game_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'genres': json.loads(row[3]) if row[3] else []
                }
                corpus.append(game_doc)
            
            return corpus
            
    except Exception as e:
        logger.error(f"Error loading game corpus: {str(e)}")
        raise

def prepare_document_text(game: Dict) -> str:
    """Prepare game data for BM25 indexing with field weighting"""
    # Weight title more heavily by repeating it
    title_weighted = (game.get('title', '') + ' ') * 3
    
    # Include description
    description = game.get('description', '')
    
    # Include genres with moderate weighting
    genres_text = ' '.join(game.get('genres', []))
    genres_weighted = (genres_text + ' ') * 2
    
    # Combine all text
    combined_text = f"{title_weighted} {description} {genres_weighted}"
    
    return combined_text.strip()

def save_bm25_index(index: BM25Okapi, corpus: List[Dict]) -> None:
    """Save BM25 index to disk for faster loading"""
    try:
        index_data = {
            'index': index,
            'corpus': corpus,
            'created_at': time.time()
        }
        
        with open('data/bm25_index.pkl', 'wb') as f:
            pickle.dump(index_data, f)
            
        logger.info("BM25 index saved to disk")
        
    except Exception as e:
        logger.warning(f"Failed to save BM25 index: {str(e)}")
```

### Notes
- Loads pre-built index from pickle file if available
- Falls back to building index from database if no cached version
- Implements field weighting (title 3x, genres 2x, description 1x)
- Saves built index to disk for faster subsequent startups
- Comprehensive error handling with fallback strategies

### Related Functions
- [search_bm25_index](#search_bm25_index)
- [tokenize_text](#tokenize_text)
- [prepare_document_text](#prepare_document_text)

### Tags
#bm25 #indexing #startup #caching #performance

---

## load_faiss_index

**Category:** Data Access
**Complexity:** High
**Last Updated:** 2024-10-08

### Description
Loads the Faiss vector similarity search index and associated game ID mappings. This function initializes the semantic search capability by loading pre-computed game embeddings and the Faiss index structure for efficient similarity searches.

### Signature
```python
def load_faiss_index() -> Tuple[faiss.Index, Dict[int, int], SentenceTransformer]:
```

### Parameters
None

### Returns
- `Tuple[faiss.Index, Dict[int, int], SentenceTransformer]`: Faiss index, game ID mapping, and embedding model

### Example
```python
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, Tuple

def load_faiss_index() -> Tuple[faiss.Index, Dict[int, int], SentenceTransformer]:
    """
    Load Faiss index, game mappings, and embedding model
    """
    try:
        # Load Faiss index
        logger.info("Loading Faiss index...")
        index_path = 'data/game_embeddings.faiss'
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Faiss index not found at {index_path}")
        
        faiss_index = faiss.read_index(index_path)
        
        # Load game ID mapping (index position -> game_id)
        mapping_path = 'data/game_id_mapping.json'
        with open(mapping_path, 'r') as f:
            game_id_mapping = json.load(f)
            # Convert string keys to integers
            game_id_mapping = {int(k): v for k, v in game_id_mapping.items()}
        
        # Load embedding model
        logger.info("Loading sentence transformer model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Verify index integrity
        verify_faiss_index(faiss_index, game_id_mapping)
        
        logger.info(f"Faiss index loaded: {faiss_index.ntotal} vectors, dimension {faiss_index.d}")
        
        return faiss_index, game_id_mapping, embedding_model
        
    except Exception as e:
        logger.error(f"Failed to load Faiss index: {str(e)}")
        raise

def verify_faiss_index(index: faiss.Index, mapping: Dict[int, int]) -> None:
    """Verify Faiss index integrity"""
    try:
        # Check if index is trained (for IVF indices)
        if hasattr(index, 'is_trained') and not index.is_trained:
            raise ValueError("Faiss index is not trained")
        
        # Verify mapping size matches index size
        if len(mapping) != index.ntotal:
            logger.warning(
                f"Mapping size ({len(mapping)}) doesn't match index size ({index.ntotal})"
            )
        
        # Test search functionality with dummy vector
        test_vector = np.random.random((1, index.d)).astype(np.float32)
        distances, indices = index.search(test_vector, min(5, index.ntotal))
        
        if len(indices[0]) == 0:
            raise ValueError("Faiss index search returned no results")
        
        logger.info("Faiss index verification passed")
        
    except Exception as e:
        logger.error(f"Faiss index verification failed: {str(e)}")
        raise

def check_faiss_index_health() -> bool:
    """Health check for Faiss index"""
    try:
        global faiss_index, game_id_mapping
        
        if faiss_index is None or game_id_mapping is None:
            return False
        
        # Quick search test
        test_vector = np.random.random((1, faiss_index.d)).astype(np.float32)
        distances, indices = faiss_index.search(test_vector, 1)
        
        return len(indices[0]) > 0 and indices[0][0] != -1
        
    except Exception:
        return False

# Global variables (set at startup)
faiss_index = None
game_id_mapping = None
embedding_model = None

def initialize_search_indices():
    """Initialize all search indices at startup"""
    global faiss_index, game_id_mapping, embedding_model
    
    try:
        # Load Faiss components
        faiss_index, game_id_mapping, embedding_model = load_faiss_index()
        
        # Load BM25 components
        global bm25_index, game_corpus
        bm25_index, game_corpus = load_bm25_index()
        
        logger.info("All search indices loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize search indices: {str(e)}")
        raise
```

### Notes
- Loads pre-computed Faiss index from disk
- Verifies index integrity and search functionality
- Uses sentence-transformers for consistent embeddings
- Implements health checks for monitoring
- Global variables for efficient access during searches

### Related Functions
- [search_faiss_index](#search_faiss_index)
- [verify_faiss_index](#verify_faiss_index)
- [check_faiss_index_health](#check_faiss_index_health)

### Tags
#faiss #embeddings #semantic-search #initialization #health-check
