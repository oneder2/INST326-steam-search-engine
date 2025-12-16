"""
Embedding Service for Semantic Search

This module provides text embedding generation for semantic search using
the sentence-transformers library. Embeddings are stored in PostgreSQL
using the pgvector extension.

Key Features:
- Singleton pattern for model efficiency
- Batch processing for performance
- LRU caching for query embeddings
- Weighted field importance (name > description > genres)

Model: all-MiniLM-L6-v2
- Dimensions: 384
- Speed: ~14,000 sentences/second
- Size: ~80MB
- Quality: Balanced for general use

Usage:
    from app.services.embedding_service import EmbeddingService
    
    # Encode a game
    embedding = EmbeddingService.encode_game({
        'name': 'Call of Duty',
        'short_description': 'First-person shooter',
        'genres': ['Action', 'Shooter']
    })
    
    # Encode a batch of games (more efficient)
    embeddings = EmbeddingService.encode_batch(games)
    
    # Encode a user query
    query_embedding = EmbeddingService.encode_query("action shooter")
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generate text embeddings for semantic search using pgvector
    
    This class uses a singleton pattern to avoid loading the model
    multiple times, which is expensive.
    """
    
    # Class-level model instance (singleton pattern)
    _model: Optional[SentenceTransformer] = None
    _model_name: str = 'all-MiniLM-L6-v2'
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """
        Get or initialize the embedding model (singleton)
        
        The model is loaded once and reused for all embedding operations.
        This is much more efficient than loading it every time.
        
        Returns:
            SentenceTransformer: The loaded model
        """
        if cls._model is None:
            logger.info(f"Loading embedding model: {cls._model_name}")
            logger.info("This may take a few seconds on first load...")
            
            try:
                cls._model = SentenceTransformer(cls._model_name)
                dimension = cls._model.get_sentence_embedding_dimension()
                logger.info(f"✓ Model loaded successfully (dimension: {dimension})")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        
        return cls._model
    
    @classmethod
    def get_dimension(cls) -> int:
        """
        Get embedding dimension
        
        Returns:
            int: Dimension of embedding vectors (384 for all-MiniLM-L6-v2)
        """
        return cls.get_model().get_sentence_embedding_dimension()
    
    @classmethod
    def encode_game(cls, game: Dict[str, Any]) -> List[float]:
        """
        Create embedding for a single game
        
        Combines multiple fields with weighting to create a comprehensive
        representation of the game:
        - Game name (weight: 2x) - Most important for matching
        - Short description (weight: 1x) - Context and details
        - Genres (weight: 1x) - Category information
        
        Args:
            game: Game data dict with 'name', 'short_description', 'genres'
        
        Returns:
            List of floats (384-dimensional vector)
        
        Example:
            >>> game = {
            ...     'name': 'Call of Duty',
            ...     'short_description': 'First-person shooter game',
            ...     'genres': ['Action', 'Shooter']
            ... }
            >>> embedding = EmbeddingService.encode_game(game)
            >>> len(embedding)
            384
        """
        # Extract fields with defaults
        name = game.get('name', '')
        desc = game.get('short_description', '')
        
        # Handle genres (can be list or JSONB array)
        genres = game.get('genres', [])
        if isinstance(genres, list):
            genres_text = ' '.join(genres)
        elif isinstance(genres, str):
            # If genres is a string, use as-is
            genres_text = genres
        else:
            genres_text = ''
        
        # Weighted concatenation
        # Name appears twice for 2x weight
        text = f"{name} {name} {desc} {genres_text}"
        
        # Generate embedding
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Convert to list for PostgreSQL compatibility
        return embedding.tolist()
    
    @classmethod
    def encode_batch(
        cls,
        games: List[Dict[str, Any]],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Batch encode multiple games (more efficient than one-by-one)
        
        This method is significantly faster than calling encode_game()
        multiple times because it processes games in batches.
        
        Args:
            games: List of game data dicts
            batch_size: Number of games to encode at once (default: 32)
            show_progress: Show progress bar (default: True)
        
        Returns:
            List of embeddings (list of lists)
        
        Example:
            >>> games = [
            ...     {'name': 'Game 1', 'short_description': 'Desc 1', 'genres': ['Action']},
            ...     {'name': 'Game 2', 'short_description': 'Desc 2', 'genres': ['RPG']}
            ... ]
            >>> embeddings = EmbeddingService.encode_batch(games)
            >>> len(embeddings)
            2
            >>> len(embeddings[0])
            384
        """
        if not games:
            return []
        
        # Build text representations for all games
        texts = []
        for game in games:
            name = game.get('name', '')
            desc = game.get('short_description', '')
            
            genres = game.get('genres', [])
            if isinstance(genres, list):
                genres_text = ' '.join(genres)
            elif isinstance(genres, str):
                genres_text = genres
            else:
                genres_text = ''
            
            # Weighted concatenation
            text = f"{name} {name} {desc} {genres_text}"
            texts.append(text)
        
        # Batch encode
        model = cls.get_model()
        logger.info(f"Encoding {len(games)} games in batches of {batch_size}...")
        
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        logger.info(f"✓ Encoded {len(games)} games")
        
        # Convert to list of lists
        return [emb.tolist() for emb in embeddings]
    
    @classmethod
    @lru_cache(maxsize=1000)
    def encode_query(cls, query: str) -> List[float]:
        """
        Encode user search query (cached for performance)
        
        Query embeddings are cached because users often search for
        similar things. The cache stores up to 1000 recent queries.
        
        Args:
            query: User search string
        
        Returns:
            List of floats (384-dimensional vector)
        
        Example:
            >>> query = "action shooter multiplayer"
            >>> embedding = EmbeddingService.encode_query(query)
            >>> len(embedding)
            384
        
        Note:
            This method is cached using @lru_cache. Identical queries
            will return the same embedding instantly without recomputing.
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to encode_query")
            # Return zero vector for empty query
            dimension = cls.get_dimension()
            return [0.0] * dimension
        
        model = cls.get_model()
        embedding = model.encode(query, convert_to_numpy=True)
        
        return embedding.tolist()
    
    @classmethod
    def clear_cache(cls):
        """
        Clear the query embedding cache
        
        Useful for testing or when memory is constrained.
        """
        cls.encode_query.cache_clear()
        logger.info("Cleared query embedding cache")
    
    @classmethod
    def get_cache_info(cls):
        """
        Get cache statistics
        
        Returns:
            CacheInfo: Named tuple with hits, misses, maxsize, currsize
        """
        return cls.encode_query.cache_info()


# Convenience function for backward compatibility
def get_embedding(text: str) -> List[float]:
    """
    Get embedding for arbitrary text (convenience function)
    
    Args:
        text: Text to embed
    
    Returns:
        List of floats (384-dimensional vector)
    """
    return EmbeddingService.encode_query(text)

