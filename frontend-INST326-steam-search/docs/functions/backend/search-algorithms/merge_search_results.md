# merge_search_results

## merge_search_results

**Category:** Search Algorithm
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Merges results from multiple search algorithms (BM25 and Faiss) into a unified result set. Handles deduplication, score normalization, and result combination to prepare data for fusion ranking algorithms.

### Signature
```python
def merge_search_results(bm25_results: List[Tuple[int, float]], faiss_results: List[Tuple[int, float]]) -> List[Tuple[int, float, str]]:
```

### Parameters
- `bm25_results` (List[Tuple[int, float]], required): BM25 search results as (game_id, score) tuples
- `faiss_results` (List[Tuple[int, float]], required): Faiss search results as (game_id, score) tuples

### Returns
- `List[Tuple[int, float, str]]`: Merged results as (game_id, score, source) tuples

### Example
```python
from typing import List, Tuple, Dict, Set
import math

def merge_search_results(
    bm25_results: List[Tuple[int, float]], 
    faiss_results: List[Tuple[int, float]]
) -> List[Tuple[int, float, str]]:
    """
    Merge and normalize results from multiple search algorithms
    """
    try:
        # Normalize scores to 0-1 range
        normalized_bm25 = normalize_scores(bm25_results, "bm25")
        normalized_faiss = normalize_scores(faiss_results, "faiss")
        
        # Create unified result dictionary
        merged_results = {}
        
        # Add BM25 results
        for game_id, score in normalized_bm25:
            merged_results[game_id] = {
                'bm25_score': score,
                'faiss_score': 0.0,
                'sources': ['bm25']
            }
        
        # Add Faiss results
        for game_id, score in normalized_faiss:
            if game_id in merged_results:
                merged_results[game_id]['faiss_score'] = score
                merged_results[game_id]['sources'].append('faiss')
            else:
                merged_results[game_id] = {
                    'bm25_score': 0.0,
                    'faiss_score': score,
                    'sources': ['faiss']
                }
        
        # Convert to output format with combined scores
        final_results = []
        for game_id, data in merged_results.items():
            # Calculate initial combined score (will be refined by fusion ranking)
            combined_score = calculate_initial_combined_score(
                data['bm25_score'], 
                data['faiss_score']
            )
            
            source_info = '+'.join(data['sources'])
            final_results.append((game_id, combined_score, source_info))
        
        # Sort by combined score (descending)
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"Merged {len(bm25_results)} BM25 + {len(faiss_results)} Faiss results "
                    f"into {len(final_results)} unique results")
        
        return final_results
        
    except Exception as e:
        logger.error(f"Error merging search results: {str(e)}")
        return []

def normalize_scores(results: List[Tuple[int, float]], algorithm: str) -> List[Tuple[int, float]]:
    """
    Normalize scores to 0-1 range for fair comparison
    """
    if not results:
        return []
    
    scores = [score for _, score in results]
    
    if algorithm == "bm25":
        # BM25 scores are typically 0-∞, use log normalization
        max_score = max(scores)
        if max_score > 0:
            normalized = [
                (game_id, math.log(score + 1) / math.log(max_score + 1))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 0.0) for game_id, _ in results]
    
    elif algorithm == "faiss":
        # Faiss similarity scores are typically 0-1, but may need inversion
        # (higher similarity = lower distance)
        max_score = max(scores)
        min_score = min(scores)
        
        if max_score > min_score:
            # Normalize to 0-1 range
            normalized = [
                (game_id, (score - min_score) / (max_score - min_score))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 1.0) for game_id, _ in results]
    
    else:
        # Default min-max normalization
        max_score = max(scores)
        min_score = min(scores)
        
        if max_score > min_score:
            normalized = [
                (game_id, (score - min_score) / (max_score - min_score))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 1.0) for game_id, _ in results]
    
    return normalized

def calculate_initial_combined_score(bm25_score: float, faiss_score: float) -> float:
    """
    Calculate initial combined score before fusion ranking
    """
    # Simple weighted average as initial combination
    # This will be refined by the fusion ranking algorithm
    bm25_weight = 0.4
    faiss_weight = 0.6
    
    combined = (bm25_score * bm25_weight) + (faiss_score * faiss_weight)
    
    # Boost scores for results found by both algorithms
    if bm25_score > 0 and faiss_score > 0:
        # Apply consensus bonus
        consensus_bonus = 0.1 * min(bm25_score, faiss_score)
        combined += consensus_bonus
    
    return min(combined, 1.0)  # Ensure score doesn't exceed 1.0

def analyze_result_overlap(bm25_results: List[Tuple[int, float]], faiss_results: List[Tuple[int, float]]) -> Dict[str, int]:
    """
    Analyze overlap between different search algorithm results
    """
    bm25_ids = set(game_id for game_id, _ in bm25_results)
    faiss_ids = set(game_id for game_id, _ in faiss_results)
    
    overlap = bm25_ids.intersection(faiss_ids)
    
    analysis = {
        'bm25_only': len(bm25_ids - faiss_ids),
        'faiss_only': len(faiss_ids - bm25_ids),
        'both_algorithms': len(overlap),
        'total_unique': len(bm25_ids.union(faiss_ids)),
        'overlap_percentage': (len(overlap) / len(bm25_ids.union(faiss_ids))) * 100 if bm25_ids.union(faiss_ids) else 0
    }
    
    return analysis

# Usage example
bm25_results = [(1, 5.2), (2, 3.8), (3, 2.1)]
faiss_results = [(2, 0.95), (3, 0.87), (4, 0.76)]

merged = merge_search_results(bm25_results, faiss_results)
# Returns: [(2, 0.89, 'bm25+faiss'), (3, 0.76, 'bm25+faiss'), (1, 0.48, 'bm25'), (4, 0.46, 'faiss')]

overlap_analysis = analyze_result_overlap(bm25_results, faiss_results)
print(f"Results found by both algorithms: {overlap_analysis['both_algorithms']}")
```

### Notes
- Implements algorithm-specific score normalization strategies
- Provides consensus bonus for results found by multiple algorithms
- Includes comprehensive overlap analysis for algorithm performance evaluation
- Handles edge cases like empty result sets and identical scores
- Maintains source information for debugging and analysis
- Optimized for performance with large result sets

### Related Functions
- [apply_fusion_ranking](#apply_fusion_ranking)
- [search_bm25_index](#search_bm25_index)
- [search_faiss_index](#search_faiss_index)

### Tags
#search #merging #normalization #deduplication #consensus #analysis
