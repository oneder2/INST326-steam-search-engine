# apply_fusion_ranking

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
