# search_bm25_index

## search_bm25_index

**Category:** Search Algorithm
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Performs BM25 keyword search on the game index to find games matching user query terms. Implements the BM25 ranking function with optimized parameters for game search, considering title, description, and genre fields with different weights.

### Signature
```python
async def search_bm25_index(query: str, limit: int = 50) -> List[BM25Result]:
```

### Parameters
- `query` (str, required): Cleaned search query text
- `limit` (int, optional): Maximum number of results to return (default: 50)

### Returns
- `List[BM25Result]`: List of search results containing:
  - `game_id` (int): Steam game ID
  - `score` (float): BM25 relevance score
  - `matched_fields` (List[str]): Fields that matched the query

### Example
```python
from rank_bm25 import BM25Okapi
import asyncio

# Global BM25 index (loaded at startup)
bm25_index = None
game_corpus = None

async def search_bm25_index(query: str, limit: int = 50) -> List[BM25Result]:
    """
    Search games using BM25 algorithm
    """
    try:
        # Tokenize query
        query_tokens = tokenize_text(query)
        
        # Get BM25 scores for all documents
        scores = bm25_index.get_scores(query_tokens)
        
        # Get top results with scores
        top_indices = scores.argsort()[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include positive scores
                game_id = game_corpus[idx]['game_id']
                
                # Determine which fields matched
                matched_fields = get_matched_fields(
                    query_tokens, 
                    game_corpus[idx]
                )
                
                results.append(BM25Result(
                    game_id=game_id,
                    score=float(scores[idx]),
                    matched_fields=matched_fields
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"BM25 search error: {str(e)}")
        return []

def tokenize_text(text: str) -> List[str]:
    """Tokenize text for BM25 search"""
    # Remove punctuation and convert to lowercase
    import re
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split and filter out short tokens
    tokens = [token for token in text.split() if len(token) > 2]
    
    return tokens

def get_matched_fields(query_tokens: List[str], game_doc: dict) -> List[str]:
    """Determine which game fields matched the query"""
    matched_fields = []
    
    # Check title
    title_tokens = tokenize_text(game_doc.get('title', ''))
    if any(token in title_tokens for token in query_tokens):
        matched_fields.append('title')
    
    # Check description
    desc_tokens = tokenize_text(game_doc.get('description', ''))
    if any(token in desc_tokens for token in query_tokens):
        matched_fields.append('description')
    
    # Check genres
    genres_text = ' '.join(game_doc.get('genres', []))
    genre_tokens = tokenize_text(genres_text)
    if any(token in genre_tokens for token in query_tokens):
        matched_fields.append('genres')
    
    return matched_fields
```

### Notes
- BM25 parameters: k1=1.5, b=0.75 (optimized for game search)
- Title matches weighted 2x higher than description matches
- Genre matches weighted 1.5x higher than description matches
- Minimum score threshold applied to filter irrelevant results
- Index loaded once at startup for optimal performance

### Related Functions
- [load_bm25_index](#load_bm25_index)
- [tokenize_text](#tokenize_text)
- [apply_fusion_ranking](#apply_fusion_ranking)

### Tags
#bm25 #keyword-search #ranking #algorithm #async

---
