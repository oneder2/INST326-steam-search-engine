# clear_search_cache

## clear_search_cache

**Category:** Caching
**Complexity:** Low
**Last Updated:** 2024-10-11

### Description
Clears the search results cache either completely or selectively based on patterns. Useful for cache invalidation when data is updated or for memory management during high-traffic periods.

### Signature
```python
async def clear_search_cache(pattern: Optional[str] = None, force: bool = False) -> int:
```

### Parameters
- `pattern` (Optional[str], optional): Pattern to match cache keys for selective clearing (default: None for all)
- `force` (bool, optional): Force clear even if cache is actively being used (default: False)

### Returns
- `int`: Number of cache entries cleared

### Example
```python
import re
import asyncio
from typing import Optional

async def clear_search_cache(pattern: Optional[str] = None, force: bool = False) -> int:
    """
    Clear search cache entries based on pattern or clear all
    """
    try:
        cleared_count = 0
        
        if pattern is None:
            # Clear all cache entries
            cleared_count = len(search_cache._cache)
            search_cache._cache.clear()
            search_cache._access_times.clear()
            logger.info(f"Cleared all {cleared_count} cache entries")
        else:
            # Clear entries matching pattern
            keys_to_remove = []
            
            # Compile regex pattern for efficient matching
            try:
                regex_pattern = re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {pattern}, error: {str(e)}")
                return 0
            
            # Find matching keys
            for key in list(search_cache._cache.keys()):
                if regex_pattern.search(key):
                    keys_to_remove.append(key)
            
            # Remove matching entries
            for key in keys_to_remove:
                await search_cache._remove(key)
                cleared_count += 1
            
            logger.info(f"Cleared {cleared_count} cache entries matching pattern: {pattern}")
        
        return cleared_count
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return 0

async def clear_expired_cache_entries() -> int:
    """
    Clear only expired cache entries
    """
    try:
        initial_count = len(search_cache._cache)
        await search_cache._cleanup_expired()
        cleared_count = initial_count - len(search_cache._cache)
        
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} expired cache entries")
        
        return cleared_count
        
    except Exception as e:
        logger.error(f"Failed to clear expired entries: {str(e)}")
        return 0

async def get_cache_stats() -> dict:
    """
    Get cache statistics for monitoring
    """
    try:
        current_time = time.time()
        total_entries = len(search_cache._cache)
        expired_entries = 0
        
        # Count expired entries
        for entry in search_cache._cache.values():
            if current_time > entry['expires_at']:
                expired_entries += 1
        
        # Calculate cache hit rate (simplified)
        active_entries = total_entries - expired_entries
        
        stats = {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'max_size': search_cache._max_size,
            'utilization_percent': (total_entries / search_cache._max_size) * 100,
            'memory_usage_mb': estimate_cache_memory_usage()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        return {}

def estimate_cache_memory_usage() -> float:
    """
    Estimate cache memory usage in MB
    """
    try:
        import sys
        total_size = 0
        
        # Estimate size of cache data
        for key, entry in search_cache._cache.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(entry)
            total_size += sys.getsizeof(entry['value'])
        
        # Add access times dictionary
        for key, timestamp in search_cache._access_times.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(timestamp)
        
        return total_size / (1024 * 1024)  # Convert to MB
        
    except Exception:
        return 0.0

async def schedule_cache_cleanup():
    """
    Schedule periodic cache cleanup task
    """
    while True:
        try:
            # Clean expired entries every 5 minutes
            await asyncio.sleep(300)
            cleared = await clear_expired_cache_entries()
            
            # Log cache statistics
            stats = await get_cache_stats()
            if stats:
                logger.debug(f"Cache stats: {stats['active_entries']}/{stats['total_entries']} active, "
                           f"{stats['utilization_percent']:.1f}% utilization, "
                           f"{stats['memory_usage_mb']:.2f}MB")
            
        except asyncio.CancelledError:
            logger.info("Cache cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# Usage examples
# Clear all cache
cleared = await clear_search_cache()

# Clear cache entries for specific queries
cleared = await clear_search_cache(pattern=r"action.*games")

# Clear only expired entries
cleared = await clear_expired_cache_entries()

# Get cache statistics
stats = await get_cache_stats()
print(f"Cache utilization: {stats['utilization_percent']:.1f}%")
```

### Notes
- Supports both complete and selective cache clearing
- Uses regex patterns for flexible cache key matching
- Includes cache statistics and monitoring capabilities
- Provides automatic cleanup scheduling for expired entries
- Memory usage estimation for performance monitoring
- Comprehensive error handling and logging

### Related Functions
- [cache_search_results](#cache_search_results)
- [get_cached_search_results](#get_cached_search_results)
- [get_cache_stats](#get_cache_stats)

### Tags
#caching #cleanup #memory-management #monitoring #regex #async
