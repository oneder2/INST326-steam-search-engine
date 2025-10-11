# load_faiss_index

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
