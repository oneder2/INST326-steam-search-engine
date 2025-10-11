# load_bm25_index

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
