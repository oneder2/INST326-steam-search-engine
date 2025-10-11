# cache_search_results

## cache_search_results

**Category:** Caching
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Caches search results to improve response times for frequently requested queries. Implements intelligent cache management with TTL (Time To Live), cache invalidation, and memory-efficient storage for optimal performance.

### Signature
```python
async def cache_search_results(query_hash: str, results: List[GameResult], ttl: int = 3600) -> bool:
```

### Parameters
- `query_hash` (str, required): Unique hash of the search query and filters
- `results` (List[GameResult], required): Search results to cache
- `ttl` (int, optional): Time to live in seconds (default: 3600 = 1 hour)

### Returns
- `bool`: True if caching was successful, False otherwise

### Example
```python
import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import asdict

class SearchCache:
    """In-memory search results cache with TTL support"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._access_times: Dict[str, float] = {}
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store value in cache with TTL"""
        try:
            # Clean expired entries if cache is getting full
            if len(self._cache) >= self._max_size:
                await self._cleanup_expired()
            
            # If still full, remove least recently used
            if len(self._cache) >= self._max_size:
                await self._evict_lru()
            
            # Store the value with metadata
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            self._access_times[key] = time.time()
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if not expired"""
        try:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if time.time() > entry['expires_at']:
                await self._remove(key)
                return None
            
            # Update access time
            self._access_times[key] = time.time()
            
            return entry['value']
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def _cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            await self._remove(key)
    
    async def _evict_lru(self) -> None:
        """Remove least recently used entry"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        await self._remove(lru_key)
    
    async def _remove(self, key: str) -> None:
        """Remove entry from cache"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)

# Global cache instance
search_cache = SearchCache(max_size=1000)

async def cache_search_results(query_hash: str, results: List[GameResult], ttl: int = 3600) -> bool:
    """
    Cache search results for improved performance
    """
    try:
        # Convert results to serializable format
        serializable_results = [
            {
                'id': result.id,
                'title': result.title,
                'score': result.score,
                'price': result.price,
                'genres': result.genres,
                'review_status': result.review_status,
                'deck_compatible': result.deck_compatible
            }
            for result in results
        ]
        
        # Store in cache
        success = await search_cache.set(query_hash, serializable_results, ttl)
        
        if success:
            logger.debug(f"Cached {len(results)} search results for query hash: {query_hash[:8]}...")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to cache search results: {str(e)}")
        return False

async def get_cached_search_results(query_hash: str) -> Optional[List[GameResult]]:
    """
    Retrieve cached search results
    """
    try:
        cached_data = await search_cache.get(query_hash)
        
        if cached_data is None:
            return None
        
        # Convert back to GameResult objects
        results = [
            GameResult(
                id=item['id'],
                title=item['title'],
                score=item['score'],
                price=item['price'],
                genres=item['genres'],
                review_status=item['review_status'],
                deck_compatible=item['deck_compatible']
            )
            for item in cached_data
        ]
        
        logger.debug(f"Retrieved {len(results)} cached results for query hash: {query_hash[:8]}...")
        return results
        
    except Exception as e:
        logger.error(f"Failed to retrieve cached results: {str(e)}")
        return None

def generate_query_hash(query: str, filters: Optional[dict] = None, limit: int = 20, offset: int = 0) -> str:
    """
    Generate unique hash for search query and parameters
    """
    # Create a consistent string representation
    query_data = {
        'query': query.lower().strip(),
        'filters': filters or {},
        'limit': limit,
        'offset': offset
    }
    
    # Convert to JSON string with sorted keys for consistency
    query_string = json.dumps(query_data, sort_keys=True)
    
    # Generate SHA-256 hash
    return hashlib.sha256(query_string.encode('utf-8')).hexdigest()

# Usage example
query_hash = generate_query_hash("action games", {"price_max": 30}, 20, 0)
await cache_search_results(query_hash, search_results, ttl=1800)  # Cache for 30 minutes
```

### Notes
- Implements LRU (Least Recently Used) eviction policy
- Automatic cleanup of expired entries
- Memory-efficient storage with configurable size limits
- Thread-safe operations with async/await support
- Generates consistent hashes for query parameters
- Includes comprehensive error handling and logging

### Related Functions
- [get_cached_search_results](#get_cached_search_results)
- [generate_query_hash](#generate_query_hash)
- [clear_search_cache](#clear_search_cache)

### Tags
#caching #performance #memory-management #ttl #lru #async
