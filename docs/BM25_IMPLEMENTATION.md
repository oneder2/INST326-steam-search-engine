# BM25 Implementation Guide

## Overview

BM25 (Best Matching 25) is a probabilistic ranking function used in information retrieval systems. This document describes the implementation of BM25 in the Steam Game Search Engine.

## What is BM25?

BM25 is a bag-of-words retrieval function that ranks documents based on:
- **Term Frequency (TF)**: How often query terms appear in a document
- **Inverse Document Frequency (IDF)**: How rare/common terms are across all documents
- **Document Length Normalization**: Accounts for varying document lengths

## Implementation Details

### Library

We use the `rank-bm25` Python library (version 0.2.2):
```bash
pip install rank-bm25==0.2.2
```

### Architecture

**Location**: `backend/app/services/search_service.py`

**Key Components**:
1. `_tokenize()`: Tokenizes text into words
2. `_calculate_bm25_score()`: Calculates BM25 score for a game
3. Post-processing: Sorts results by BM25 score when relevance sort is selected

### Tokenization

```python
def _tokenize(self, text: str) -> List[str]:
    """Tokenize text for BM25 processing"""
    if not text:
        return []
    # Convert to lowercase and split on non-alphanumeric characters
    tokens = re.findall(r'\w+', text.lower())
    return tokens
```

**Features**:
- Case-insensitive
- Splits on non-alphanumeric characters
- Returns list of tokens

### BM25 Scoring

```python
def _calculate_bm25_score(self, game: Dict[str, Any], query: str) -> float:
    """Calculate BM25 relevance score for a game"""
    # Tokenize query
    query_tokens = self._tokenize(query)
    
    total_score = 0.0
    
    # Name field (weight: 2.0)
    name_tokens = self._tokenize(game.get('name', ''))
    bm25_name = BM25Okapi([name_tokens])
    name_score = bm25_name.get_scores(query_tokens)[0]
    total_score += name_score * 2.0
    
    # Description field (weight: 1.0)
    desc_tokens = self._tokenize(game.get('short_description', ''))
    bm25_desc = BM25Okapi([desc_tokens])
    desc_score = bm25_desc.get_scores(query_tokens)[0]
    total_score += desc_score * 1.0
    
    return round(total_score, 4)
```

**Field Weights**:
- **Name**: 2.0 (highest priority - game titles are most important)
- **Description**: 1.0 (secondary - provides context)

### Integration with Search

When `sort_by='relevance'` and a query is provided:
1. Database returns filtered results
2. BM25 score is calculated for each result
3. Results are sorted by BM25 score (descending)
4. Sorted results are returned to frontend

```python
# Post-processing: Sort by BM25 score if relevance sort
if sort_by == SortBy.RELEVANCE and query.strip():
    results.sort(key=lambda x: x['bm25_score'], reverse=True)
```

## Configuration

BM25 behavior can be configured in `backend/app/config.py`:

```python
BM25_ENABLED: bool = True
"""Enable BM25 ranking algorithm"""

BM25_NAME_WEIGHT: float = 2.0
"""Weight for game name field"""

BM25_DESCRIPTION_WEIGHT: float = 1.0
"""Weight for game description field"""
```

## API Response

Search results now include both scoring methods:

```json
{
  "results": [
    {
      "game_id": 570,
      "title": "Dota 2",
      "relevance_score": 0.85,  // Simple scoring (backward compatible)
      "bm25_score": 2.4567       // BM25 score (new)
    }
  ]
}
```

## Performance Considerations

### Current Implementation
- BM25 is calculated **per-result** after database query
- Suitable for small to medium result sets (< 1000 results)
- No pre-computed index

### Optimization Opportunities (Future)
1. **Pre-compute BM25 index**: Build index for entire corpus
2. **Cache common queries**: Store BM25 scores for frequent searches
3. **Batch processing**: Calculate BM25 for multiple documents at once
4. **Database-level scoring**: Use PostgreSQL full-text search features

## Testing

### Unit Test

```python
# Test BM25 scoring
game = {
    'name': 'Counter-Strike Global Offensive',
    'short_description': 'Tactical first-person shooter game.'
}

score = service._calculate_bm25_score(game, 'counter strike')
# Expected: Positive score for matching terms
```

### Integration Test

```bash
# Test search with BM25
curl -X POST http://localhost:8000/api/v1/search/games \
  -H "Content-Type: application/json" \
  -d '{
    "query": "action",
    "sort_by": "relevance",
    "limit": 5
  }'
```

## Comparison: Simple vs BM25

### Simple Scoring (Phase 2)
- **Method**: String matching with weights
- **Pros**: Fast, predictable
- **Cons**: Doesn't account for term rarity

### BM25 Scoring (Phase 3)
- **Method**: Probabilistic ranking
- **Pros**: Better relevance, accounts for term frequency and rarity
- **Cons**: Slightly slower, more complex

## Example Results

**Query**: "action"

| Game | Simple Score | BM25 Score | Notes |
|------|-------------|------------|-------|
| Act of War | 0.67 | -0.824 | "action" in title |
| Action Game | 0.20 | -0.275 | "action" in description |

*Note: Negative BM25 scores are normal when scoring individual documents*

## Future Enhancements

1. **Tunable Parameters**: Expose k1 and b parameters for BM25
2. **Field Boosting**: Allow dynamic field weight adjustment
3. **Query Expansion**: Add synonyms and related terms
4. **Personalization**: Adjust scores based on user preferences

## References

- [BM25 Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
- [rank-bm25 Library](https://github.com/dorianbrown/rank_bm25)
- [Information Retrieval: BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)

---

**Last Updated**: 2024-12-16  
**Version**: 1.1.0  
**Phase**: 3 (Complete)

