# search_faiss_index

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
