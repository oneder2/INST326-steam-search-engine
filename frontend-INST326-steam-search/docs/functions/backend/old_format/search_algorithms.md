# FastAPI Backend - Search Algorithms

This document contains documentation for search and ranking algorithm functions in the Python FastAPI backend.

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

## search_faiss_index

**Category:** Search Algorithm
**Complexity:** High
**Last Updated:** 2024-10-08

### Description
Performs semantic search using Faiss vector similarity search on game embeddings. Converts user query to vector embedding and finds semantically similar games using cosine similarity in the embedding space.

### Signature
```python
async def search_faiss_index(query: str, limit: int = 50) -> List[FaissResult]:
```

### Parameters
- `query` (str, required): User search query
- `limit` (int, optional): Maximum number of results (default: 50)

### Returns
- `List[FaissResult]`: Semantic search results containing:
  - `game_id` (int): Steam game ID
  - `similarity_score` (float): Cosine similarity score (0.0 - 1.0)
  - `embedding_distance` (float): L2 distance in embedding space

### Example
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Global variables (loaded at startup)
faiss_index = None
game_id_mapping = None
embedding_model = None

async def search_faiss_index(query: str, limit: int = 50) -> List[FaissResult]:
    """
    Perform semantic search using Faiss vector index
    """
    try:
        # Generate query embedding
        query_embedding = await generate_query_embedding(query)
        
        # Search Faiss index
        distances, indices = faiss_index.search(
            query_embedding.reshape(1, -1), 
            limit
        )
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid result
                game_id = game_id_mapping[idx]
                
                # Convert L2 distance to cosine similarity
                similarity_score = distance_to_similarity(distance)
                
                results.append(FaissResult(
                    game_id=game_id,
                    similarity_score=similarity_score,
                    embedding_distance=float(distance)
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"Faiss search error: {str(e)}")
        return []

async def generate_query_embedding(query: str) -> np.ndarray:
    """Generate embedding for search query"""
    try:
        # Use sentence transformer model
        embedding = embedding_model.encode([query])
        return embedding[0].astype(np.float32)
        
    except Exception as e:
        logger.error(f"Embedding generation error: {str(e)}")
        # Return zero vector as fallback
        return np.zeros(384, dtype=np.float32)

def distance_to_similarity(l2_distance: float) -> float:
    """Convert L2 distance to cosine similarity score"""
    # Assuming normalized vectors, L2 distance relates to cosine similarity
    # similarity = 1 - (distance^2 / 2)
    similarity = max(0.0, 1.0 - (l2_distance ** 2 / 2.0))
    return min(1.0, similarity)

def load_faiss_index() -> tuple:
    """Load Faiss index and related data at startup"""
    try:
        # Load Faiss index
        index = faiss.read_index("data/game_embeddings.faiss")
        
        # Load game ID mapping
        with open("data/game_id_mapping.json", "r") as f:
            id_mapping = json.load(f)
        
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info(f"Loaded Faiss index with {index.ntotal} vectors")
        return index, id_mapping, model
        
    except Exception as e:
        logger.error(f"Failed to load Faiss index: {str(e)}")
        raise
```

### Notes
- Uses sentence-transformers model 'all-MiniLM-L6-v2' for embeddings
- Faiss index built with IVF (Inverted File) for faster search
- Embeddings normalized for cosine similarity computation
- Handles edge cases like empty queries and model failures
- Index loaded once at startup to avoid repeated loading overhead

### Related Functions
- [load_faiss_index](#load_faiss_index)
- [generate_query_embedding](#generate_query_embedding)
- [apply_fusion_ranking](#apply_fusion_ranking)

### Tags
#faiss #semantic-search #embeddings #vector-similarity #async

---

## apply_fusion_ranking

**Category:** Search Algorithm
**Complexity:** High
**Last Updated:** 2024-10-08

### Description
Implements the core fusion ranking algorithm that combines BM25 keyword scores, Faiss semantic scores, and game quality metrics to produce the final ranking. Uses weighted linear combination with normalization to ensure balanced scoring.

### Signature
```python
async def apply_fusion_ranking(
    bm25_results: List[BM25Result],
    faiss_results: List[FaissResult],
    quality_metrics: Dict[int, RankingMetrics]
) -> List[FusionResult]:
```

### Parameters
- `bm25_results` (List[BM25Result]): BM25 keyword search results
- `faiss_results` (List[FaissResult]): Faiss semantic search results
- `quality_metrics` (Dict[int, RankingMetrics]): Game quality metrics by game_id

### Returns
- `List[FusionResult]`: Final ranked results containing:
  - `game_id` (int): Steam game ID
  - `final_score` (float): Combined ranking score (0.0 - 1.0)
  - `component_scores` (dict): Individual score components for debugging

### Example
```python
from typing import Dict, List
import numpy as np

# Fusion ranking weights (configurable)
FUSION_WEIGHTS = {
    "bm25_weight": 0.35,
    "semantic_weight": 0.35,
    "quality_weight": 0.30
}

async def apply_fusion_ranking(
    bm25_results: List[BM25Result],
    faiss_results: List[FaissResult],
    quality_metrics: Dict[int, RankingMetrics]
) -> List[FusionResult]:
    """
    Apply fusion ranking algorithm to combine multiple relevance signals
    """
    try:
        # 1. Merge results from both search methods
        all_game_ids = set()
        bm25_scores = {}
        faiss_scores = {}
        
        # Collect BM25 scores
        for result in bm25_results:
            all_game_ids.add(result.game_id)
            bm25_scores[result.game_id] = result.score
        
        # Collect Faiss scores
        for result in faiss_results:
            all_game_ids.add(result.game_id)
            faiss_scores[result.game_id] = result.similarity_score
        
        # 2. Normalize scores to [0, 1] range
        normalized_bm25 = normalize_scores(bm25_scores)
        normalized_faiss = normalize_scores(faiss_scores)
        
        # 3. Calculate fusion scores for each game
        fusion_results = []
        
        for game_id in all_game_ids:
            # Get normalized component scores
            bm25_score = normalized_bm25.get(game_id, 0.0)
            semantic_score = normalized_faiss.get(game_id, 0.0)
            
            # Get quality score
            quality_score = 0.0
            if game_id in quality_metrics:
                metrics = quality_metrics[game_id]
                quality_score = calculate_quality_score(metrics)
            
            # Apply fusion formula
            final_score = (
                FUSION_WEIGHTS["bm25_weight"] * bm25_score +
                FUSION_WEIGHTS["semantic_weight"] * semantic_score +
                FUSION_WEIGHTS["quality_weight"] * quality_score
            )
            
            fusion_results.append(FusionResult(
                game_id=game_id,
                final_score=final_score,
                component_scores={
                    "bm25": bm25_score,
                    "semantic": semantic_score,
                    "quality": quality_score
                }
            ))
        
        # 4. Sort by final score (descending)
        fusion_results.sort(key=lambda x: x.final_score, reverse=True)
        
        return fusion_results
        
    except Exception as e:
        logger.error(f"Fusion ranking error: {str(e)}")
        return []

def normalize_scores(scores: Dict[int, float]) -> Dict[int, float]:
    """Normalize scores to [0, 1] range using min-max normalization"""
    if not scores:
        return {}
    
    values = list(scores.values())
    min_score = min(values)
    max_score = max(values)
    
    # Avoid division by zero
    if max_score == min_score:
        return {game_id: 1.0 for game_id in scores}
    
    normalized = {}
    for game_id, score in scores.items():
        normalized[game_id] = (score - min_score) / (max_score - min_score)
    
    return normalized

def calculate_quality_score(metrics: RankingMetrics) -> float:
    """Calculate composite quality score from ranking metrics"""
    # Use geometric mean to balance review stability and player activity
    review_stability = metrics.review_stability
    player_activity = metrics.player_activity
    
    # Geometric mean with slight bias toward review stability
    quality_score = (review_stability ** 0.6) * (player_activity ** 0.4)
    
    return min(1.0, max(0.0, quality_score))
```

### Notes
- Default weights: BM25 (35%), Semantic (35%), Quality (30%)
- Uses min-max normalization to ensure fair score combination
- Geometric mean for quality score prevents games with one poor metric from ranking highly
- Configurable weights allow tuning for different use cases
- Comprehensive logging for debugging ranking decisions

### Related Functions
- [search_bm25_index](#search_bm25_index)
- [search_faiss_index](#search_faiss_index)
- [calculate_quality_score](#calculate_quality_score)
- [normalize_scores](#normalize_scores)

### Tags
#fusion-ranking #algorithm #scoring #normalization #quality-metrics

---

## validate_search_query

**Category:** Validation
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Validates and sanitizes user search input to prevent injection attacks and ensure query compatibility with search algorithms. Performs comprehensive input validation including length checks, character filtering, and malicious pattern detection.

### Signature
```python
def validate_search_query(query: str) -> str:
```

### Parameters
- `query` (str, required): Raw user search input

### Returns
- `str`: Cleaned and validated search query

### Example
```python
import re
from typing import List

# Security patterns to detect and remove
MALICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',                # JavaScript URLs
    r'on\w+\s*=',                 # Event handlers
    r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
    r'eval\s*\(',                 # Eval functions
    r'document\.',                # DOM access
]

def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query input
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    # 1. Length validation
    if len(query) > 500:
        raise ValueError("Query exceeds maximum length of 500 characters")
    
    if len(query.strip()) < 1:
        raise ValueError("Query cannot be empty")
    
    # 2. Remove malicious patterns
    cleaned_query = query
    for pattern in MALICIOUS_PATTERNS:
        cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.IGNORECASE)
    
    # 3. Remove HTML tags
    cleaned_query = re.sub(r'<[^>]+>', '', cleaned_query)
    
    # 4. Normalize whitespace
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query.strip())
    
    # 5. Remove special characters (keep alphanumeric, spaces, basic punctuation)
    cleaned_query = re.sub(r'[^\w\s\-.,!?\'"]', '', cleaned_query)
    
    # 6. Final length check after cleaning
    if len(cleaned_query.strip()) < 1:
        raise ValueError("Query contains no valid search terms")
    
    return cleaned_query

def detect_sql_injection(query: str) -> bool:
    """Detect potential SQL injection patterns"""
    sql_patterns = [
        r'\b(union|select|insert|update|delete|drop|create|alter)\b',
        r'[\'";]',
        r'--',
        r'/\*.*?\*/',
        r'\bor\b.*?=.*?=',
        r'\band\b.*?=.*?='
    ]
    
    query_lower = query.lower()
    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

# Usage in FastAPI endpoint
@app.post("/api/v1/search/games")
async def search_games(query: SearchQuerySchema):
    try:
        # Validate search query
        clean_query = validate_search_query(query.query)
        
        # Check for SQL injection
        if detect_sql_injection(clean_query):
            logger.warning(f"Potential SQL injection detected: {query.query}")
            raise HTTPException(status_code=400, detail="Invalid query format")
        
        # Proceed with search...
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Notes
- Maximum query length: 500 characters
- Removes HTML tags, script elements, and event handlers
- Preserves Unicode characters for international search terms
- Logs suspicious queries for security monitoring
- Raises HTTPException with appropriate status codes for FastAPI

### Related Functions
- [detect_sql_injection](#detect_sql_injection)
- [sanitize_input](#sanitize_input)
- [search_games](#search_games)

### Tags
#validation #security #sanitization #sql-injection #xss
